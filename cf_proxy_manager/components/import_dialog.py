"""V2Ray 订阅导入对话框

提供导入 V2Ray 订阅链接的 UI 界面。
"""

import customtkinter as ctk
from typing import Callable
import threading

from cf_proxy_manager.v2ray_parser import V2RayParser, ParsedNode
from cf_proxy_manager.dns_resolver import DNSResolver
from cf_proxy_manager.logger import logger
from cf_proxy_manager.components.theme import AppTheme


class ImportDialog(ctk.CTkToplevel):
    """V2Ray 订阅导入对话框"""
    
    def __init__(self, parent, on_import: Callable[[list[str]], None]):
        """初始化导入对话框
        
        Args:
            parent: 父窗口
            on_import: 导入回调函数，参数为 IP 列表
        """
        super().__init__(parent)
        
        self.on_import = on_import
        self.parsed_nodes: list[ParsedNode] = []
        
        # 窗口设置
        self.title("导入 V2Ray 订阅")
        self.geometry("520x550")
        self.minsize(520, 550)
        self.resizable(True, True)
        
        # 居中显示
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 520) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 550) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
        # 模态对话框
        self.transient(parent)
        self.grab_set()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            main_frame,
            text="粘贴订阅内容:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        # 文本输入框
        self.text_input = ctk.CTkTextbox(
            main_frame,
            height=180,
            font=ctk.CTkFont(size=12)
        )
        self.text_input.pack(fill="x", pady=(0, 15))
        self.text_input.bind("<KeyRelease>", self._on_text_change)
        
        # 选项区域
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.pack(fill="x", pady=(0, 15))
        
        self.resolve_dns_var = ctk.BooleanVar(value=True)
        self.resolve_dns_cb = ctk.CTkCheckBox(
            options_frame,
            text="自动解析域名为 IP",
            variable=self.resolve_dns_var,
            font=ctk.CTkFont(size=12)
        )
        self.resolve_dns_cb.pack(anchor="w", pady=2)
        
        self.skip_duplicate_var = ctk.BooleanVar(value=True)
        self.skip_duplicate_cb = ctk.CTkCheckBox(
            options_frame,
            text="跳过重复 IP",
            variable=self.skip_duplicate_var,
            font=ctk.CTkFont(size=12)
        )
        self.skip_duplicate_cb.pack(anchor="w", pady=2)
        
        # 预览区域
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="x", pady=(0, 15))
        
        preview_title = ctk.CTkLabel(
            preview_frame,
            text="预览:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        preview_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="等待输入...",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w"
        )
        self.preview_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(fill="x", pady=(0, 10))
        
        # 按钮区域 - 固定在底部
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="取消",
            width=100,
            height=36,
            fg_color="gray",
            command=self.destroy
        )
        self.cancel_btn.pack(side="right", padx=(10, 0))
        
        self.import_btn = ctk.CTkButton(
            button_frame,
            text="解析并导入",
            width=120,
            height=36,
            command=self._on_import_click
        )
        self.import_btn.pack(side="right")
    
    def _on_text_change(self, event=None):
        """文本变化时更新预览"""
        content = self.text_input.get("1.0", "end-1c")
        
        if not content.strip():
            self.preview_label.configure(text="等待输入...")
            self.parsed_nodes = []
            return
        
        # 解析内容
        self.parsed_nodes = V2RayParser.parse(content)
        
        if not self.parsed_nodes:
            self.preview_label.configure(text="未检测到有效节点")
            return
        
        # 统计 IP 和域名数量
        ip_count = sum(1 for n in self.parsed_nodes if n.is_ip)
        domain_count = len(self.parsed_nodes) - ip_count
        
        preview_text = f"检测到 {len(self.parsed_nodes)} 个节点:\n"
        preview_text += f"• IP 地址: {ip_count} 个\n"
        preview_text += f"• 域名: {domain_count} 个"
        if domain_count > 0:
            preview_text += " (待解析)"
        
        self.preview_label.configure(text=preview_text)
    
    def _on_import_click(self):
        """点击导入按钮"""
        if not self.parsed_nodes:
            self.status_label.configure(text="没有可导入的节点", text_color="red")
            return
        
        # 禁用按钮
        self.import_btn.configure(state="disabled")
        self.cancel_btn.configure(state="disabled")
        self.status_label.configure(text="正在处理...", text_color="gray")
        
        # 在后台线程执行导入
        thread = threading.Thread(target=self._do_import, daemon=True)
        thread.start()
    
    def _do_import(self):
        """执行导入操作（后台线程）"""
        try:
            ips = []
            
            # 收集 IP 地址
            for node in self.parsed_nodes:
                if node.is_ip:
                    ips.append(node.address)
            
            # 解析域名
            if self.resolve_dns_var.get():
                domains = [n.address for n in self.parsed_nodes if not n.is_ip]
                if domains:
                    self.after(0, lambda: self.status_label.configure(
                        text=f"正在解析 {len(domains)} 个域名..."
                    ))
                    
                    results = DNSResolver.resolve_batch(domains)
                    for domain, resolved_ips in results.items():
                        ips.extend(resolved_ips)
            
            # 去重
            if self.skip_duplicate_var.get():
                ips = list(dict.fromkeys(ips))  # 保持顺序的去重
            
            logger.info(f"导入对话框: 准备导入 {len(ips)} 个 IP")
            
            # 在主线程调用回调
            self.after(0, lambda: self._finish_import(ips))
            
        except Exception as e:
            logger.error(f"导入失败: {e}")
            self.after(0, lambda: self._show_error(str(e)))
    
    def _finish_import(self, ips: list[str]):
        """完成导入（主线程）"""
        if ips:
            self.on_import(ips)
        self.destroy()
    
    def _show_error(self, message: str):
        """显示错误信息"""
        self.status_label.configure(text=f"错误: {message}", text_color="red")
        self.import_btn.configure(state="normal")
        self.cancel_btn.configure(state="normal")
