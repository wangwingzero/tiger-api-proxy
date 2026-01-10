"""
CF Proxy Manager - CustomTkinter GUI
现代化图形用户界面
"""
import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Optional, List

from .models import Config, IPEntry, DEFAULT_IPS, DEFAULT_TARGET_NODE
from .config_manager import ConfigManager
from .parsers import URLParser, IPParser
from .speed_tester import SpeedTester
from .hosts_manager import HostsManager
from .admin_helper import AdminHelper
from .components.theme import AppTheme
from .components.ip_card import IPCard


class CFProxyManagerCTk(ctk.CTk):
    """CF Proxy Manager - CustomTkinter 版本"""
    
    def __init__(self):
        super().__init__()
        
        # 窗口配置
        self.title(f"🐯 虎哥API反代 v{self._get_version()}")
        self.geometry("720x800")
        self.minsize(650, 700)
        
        # 初始化组件
        self.config_manager = ConfigManager()
        self.speed_tester = SpeedTester(timeout=3.0)
        self.hosts_manager = HostsManager()
        
        # 加载配置
        self.config = self.config_manager.load()
        
        # 设置主题
        theme_mode = getattr(self.config, 'theme_mode', 'system')
        if theme_mode not in AppTheme.THEME_MODES:
            theme_mode = 'system'
        ctk.set_appearance_mode(theme_mode)
        ctk.set_default_color_theme("blue")
        
        # 测试结果缓存
        self.test_results = {}
        
        # IP 卡片列表
        self.ip_cards: List[IPCard] = []
        
        # 测速状态
        self.is_testing = False
        
        # 创建界面
        self._create_widgets()
        self._load_config_to_ui()
    
    def _create_widgets(self):
        """创建所有界面组件"""
        # 主容器
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 1. 目标反代节点区域
        self._create_target_node_section()
        
        # 2. CF 反代配置区域
        self._create_cf_proxy_section()
        
        # 3. 优选 IP 管理区域
        self._create_ip_management_section()
        
        # 4. 状态显示区域
        self._create_status_section()
    
    def _create_target_node_section(self):
        """创建目标反代节点区域"""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", pady=(0, 10))
        
        # 标题
        title = ctk.CTkLabel(frame, text="📡 目标反代节点", font=AppTheme.FONT_BOLD)
        title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # 内容行
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(row, text="当前节点:", font=AppTheme.FONT_DEFAULT).pack(side="left")
        
        self.target_node_var = ctk.StringVar()
        self.target_node_combo = ctk.CTkComboBox(
            row,
            variable=self.target_node_var,
            width=300,
            font=AppTheme.FONT_DEFAULT,
            command=self._on_target_node_changed
        )
        self.target_node_combo.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            row, text="添加", width=60,
            command=self._on_add_target_node
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            row, text="删除", width=60,
            fg_color="gray50", hover_color="gray40",
            command=self._on_delete_target_node
        ).pack(side="left", padx=2)
    
    def _create_cf_proxy_section(self):
        """创建 CF 反代配置区域"""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x", pady=(0, 10))
        
        # 标题
        title = ctk.CTkLabel(frame, text="🌐 CF 反代配置", font=AppTheme.FONT_BOLD)
        title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # 反代域名输入
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(row1, text="反代域名/URL:", font=AppTheme.FONT_DEFAULT).pack(side="left")
        
        self.cf_domain_var = ctk.StringVar()
        self.cf_domain_entry = ctk.CTkEntry(
            row1,
            textvariable=self.cf_domain_var,
            width=350,
            font=AppTheme.FONT_DEFAULT
        )
        self.cf_domain_entry.pack(side="left", padx=10, fill="x", expand=True)
        self.cf_domain_var.trace_add('write', self._on_cf_domain_changed)
        
        # 完整代理地址显示
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(row2, text="完整代理地址:", font=AppTheme.FONT_DEFAULT).pack(side="left")
        
        self.full_proxy_url_var = ctk.StringVar()
        self.full_proxy_url_label = ctk.CTkLabel(
            row2,
            textvariable=self.full_proxy_url_var,
            text_color=AppTheme.COLORS["primary"],
            font=AppTheme.FONT_DEFAULT
        )
        self.full_proxy_url_label.pack(side="left", padx=10)

    def _create_ip_management_section(self):
        """创建优选 IP 管理区域"""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # 标题
        title = ctk.CTkLabel(frame, text="📋 优选 IP 管理", font=AppTheme.FONT_BOLD)
        title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # IP 卡片列表（可滚动）
        self.ip_scroll_frame = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent"
        )
        self.ip_scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 添加 IP 输入
        add_frame = ctk.CTkFrame(frame, fg_color="transparent")
        add_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(add_frame, text="添加 IP:", font=AppTheme.FONT_DEFAULT).pack(side="left")
        
        self.add_ip_var = ctk.StringVar()
        self.add_ip_entry = ctk.CTkEntry(
            add_frame,
            textvariable=self.add_ip_var,
            width=300,
            font=AppTheme.FONT_DEFAULT,
            placeholder_text="输入 IP 地址，如 1.2.3.4:443"
        )
        self.add_ip_entry.pack(side="left", padx=10, fill="x", expand=True)
        self.add_ip_entry.bind('<Return>', lambda e: self._on_add_ip())
        
        ctk.CTkButton(
            add_frame, text="➕ 添加", width=80,
            command=self._on_add_ip
        ).pack(side="left")
        
        # 操作按钮
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        self.test_btn = ctk.CTkButton(
            btn_frame,
            text="🚀 开始测速",
            width=120,
            fg_color=AppTheme.COLORS["primary"],
            command=self._on_test_speed
        )
        self.test_btn.pack(side="left", padx=4)
        
        ctk.CTkButton(
            btn_frame,
            text="✅ 应用最佳 IP",
            width=120,
            fg_color=AppTheme.COLORS["success"],
            hover_color="#218838",
            command=self._on_apply_best_ip
        ).pack(side="left", padx=4)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ 删除选中",
            width=100,
            fg_color="gray50",
            hover_color="gray40",
            command=self._on_delete_ip
        ).pack(side="left", padx=4)
        
        ctk.CTkButton(
            btn_frame,
            text="🧹 清除hosts",
            width=100,
            fg_color=AppTheme.COLORS["danger"],
            hover_color="#c82333",
            command=self._on_clear_hosts
        ).pack(side="left", padx=4)
    
    def _create_status_section(self):
        """创建状态显示区域"""
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill="x")
        
        # 标题行
        title_row = ctk.CTkFrame(frame, fg_color="transparent")
        title_row.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(title_row, text="📊 状态", font=AppTheme.FONT_BOLD).pack(side="left")
        
        # 主题切换
        theme_frame = ctk.CTkFrame(title_row, fg_color="transparent")
        theme_frame.pack(side="right")
        
        ctk.CTkLabel(theme_frame, text="主题:", font=AppTheme.FONT_SMALL).pack(side="left", padx=5)
        
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            variable=self.theme_var,
            values=["深色", "浅色", "跟随系统"],
            width=100,
            font=AppTheme.FONT_SMALL,
            command=self._on_theme_changed
        )
        # 设置当前主题显示
        current_mode = ctk.get_appearance_mode().lower()
        if current_mode == "dark":
            self.theme_var.set("深色")
        elif current_mode == "light":
            self.theme_var.set("浅色")
        else:
            self.theme_var.set("跟随系统")
        self.theme_menu.pack(side="left")
        
        # 权限状态
        row0 = ctk.CTkFrame(frame, fg_color="transparent")
        row0.pack(fill="x", padx=15, pady=2)
        
        ctk.CTkLabel(row0, text="权限状态:", font=AppTheme.FONT_SMALL).pack(side="left")
        
        admin_color = AppTheme.COLORS["success"] if AdminHelper.is_admin() else AppTheme.COLORS["danger"]
        self.admin_status_label = ctk.CTkLabel(
            row0,
            text=AdminHelper.get_status_text(),
            text_color=admin_color,
            font=AppTheme.FONT_SMALL
        )
        self.admin_status_label.pack(side="left", padx=5)
        
        # 查看 hosts 按钮
        ctk.CTkButton(
            row0,
            text="📋 查看 hosts",
            width=100,
            height=28,
            font=AppTheme.FONT_SMALL,
            command=self._on_view_hosts
        ).pack(side="right")
        
        # 当前 hosts 配置
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=2)
        
        ctk.CTkLabel(row1, text="当前 hosts 配置:", font=AppTheme.FONT_SMALL).pack(side="left")
        
        self.hosts_status_var = ctk.StringVar(value="未配置")
        ctk.CTkLabel(
            row1,
            textvariable=self.hosts_status_var,
            font=AppTheme.FONT_SMALL
        ).pack(side="left", padx=5)
        
        # 操作状态
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=(2, 10))
        
        ctk.CTkLabel(row2, text="状态:", font=AppTheme.FONT_SMALL).pack(side="left")
        
        self.status_var = ctk.StringVar(value="就绪")
        self.status_label = ctk.CTkLabel(
            row2,
            textvariable=self.status_var,
            font=AppTheme.FONT_SMALL
        )
        self.status_label.pack(side="left", padx=5)

    def _load_config_to_ui(self):
        """将配置加载到界面"""
        # 目标节点
        if self.config.target_nodes:
            self.target_node_combo.configure(values=self.config.target_nodes)
            if self.config.current_target_node:
                self.target_node_var.set(self.config.current_target_node)
            else:
                self.target_node_var.set(self.config.target_nodes[0])
        
        # CF 反代域名
        self.cf_domain_var.set(self.config.cf_proxy_domain)
        
        # IP 列表
        self._refresh_ip_list()
        
        # 更新 hosts 状态
        self._update_hosts_status()
    
    def _refresh_ip_list(self):
        """刷新 IP 列表显示"""
        # 清空现有卡片
        for card in self.ip_cards:
            card.destroy()
        self.ip_cards.clear()
        
        # 找出最佳 IP
        best_ip = None
        if self.test_results:
            results = list(self.test_results.values())
            best_result = SpeedTester.get_best_ip(results)
            if best_result:
                best_ip = best_result.ip_entry.ip
        
        # 创建 IP 卡片
        for ip_entry in self.config.ip_list:
            result = self.test_results.get(ip_entry.ip)
            is_best = (ip_entry.ip == best_ip)
            
            card = IPCard(
                self.ip_scroll_frame,
                ip_entry=ip_entry,
                result=result,
                is_best=is_best,
                on_select=self._on_card_select
            )
            card.pack(fill="x", pady=3, padx=5)
            self.ip_cards.append(card)
        
        # 如果没有 IP，显示提示
        if not self.ip_cards:
            placeholder = ctk.CTkLabel(
                self.ip_scroll_frame,
                text="暂无 IP 地址，请添加",
                text_color="gray50",
                font=AppTheme.FONT_DEFAULT
            )
            placeholder.pack(pady=20)
    
    def _on_card_select(self, card: IPCard):
        """卡片选中回调"""
        # 可以在这里处理多选逻辑
        pass
    
    def _get_selected_cards(self) -> List[IPCard]:
        """获取选中的卡片"""
        return [card for card in self.ip_cards if card.is_selected]
    
    def _update_hosts_status(self):
        """更新 hosts 状态显示"""
        cf_domain = URLParser.extract_domain(self.cf_domain_var.get())
        if cf_domain:
            entry = self.hosts_manager.get_entry(cf_domain)
            if entry:
                self.hosts_status_var.set(f"{cf_domain} -> {entry[0]}")
            else:
                self.hosts_status_var.set(f"{cf_domain}: 未配置")
        else:
            self.hosts_status_var.set("未配置")
    
    def _update_full_proxy_url(self):
        """更新完整代理地址显示"""
        cf_input = self.cf_domain_var.get().strip()
        target = self.target_node_var.get().strip()
        
        if not cf_input:
            self.full_proxy_url_var.set("")
            return
        
        # 解析输入
        config = URLParser.parse_proxy_url(cf_input)
        if config:
            cf_domain = config.cf_domain
            if config.target_node:
                target = config.target_node
        else:
            cf_domain = cf_input
        
        full_url = URLParser.build_proxy_url(cf_domain, target)
        self.full_proxy_url_var.set(full_url)
    
    def _save_config(self):
        """保存配置"""
        self.config.current_target_node = self.target_node_var.get()
        self.config.cf_proxy_domain = self.cf_domain_var.get()
        self.config_manager.save(self.config)
    
    # 事件处理
    def _on_target_node_changed(self, value=None):
        """目标节点改变"""
        self._update_full_proxy_url()
        self._save_config()
    
    def _on_add_target_node(self):
        """添加目标节点"""
        node = self.target_node_var.get().strip()
        if not node:
            return
        
        if node not in self.config.target_nodes:
            self.config.target_nodes.append(node)
            self.target_node_combo.configure(values=self.config.target_nodes)
            self._save_config()
            self.status_var.set(f"已添加节点: {node}")
    
    def _on_delete_target_node(self):
        """删除目标节点"""
        node = self.target_node_var.get().strip()
        if node in self.config.target_nodes:
            self.config.target_nodes.remove(node)
            self.target_node_combo.configure(values=self.config.target_nodes)
            if self.config.target_nodes:
                self.target_node_var.set(self.config.target_nodes[0])
            else:
                self.target_node_var.set("")
            self._save_config()
            self.status_var.set(f"已删除节点: {node}")
    
    def _on_cf_domain_changed(self, *args):
        """CF 反代域名改变"""
        self._update_full_proxy_url()
        self._update_hosts_status()
        self.after(500, self._save_config)
    
    def _on_add_ip(self):
        """添加 IP"""
        ip_text = self.add_ip_var.get().strip()
        if not ip_text:
            return
        
        entries = IPParser.parse_multiple(ip_text)
        if not entries:
            messagebox.showerror("错误", "无效的 IP 格式")
            return
        
        added = 0
        for entry in entries:
            exists = any(e.ip == entry.ip for e in self.config.ip_list)
            if not exists:
                self.config.ip_list.append(entry)
                added += 1
        
        if added > 0:
            self._refresh_ip_list()
            self._save_config()
            self.add_ip_var.set("")
            self.status_var.set(f"已添加 {added} 个 IP")
        else:
            self.status_var.set("IP 已存在")
    
    def _on_delete_ip(self):
        """删除选中的 IP"""
        selected = self._get_selected_cards()
        if not selected:
            messagebox.showinfo("提示", "请先选中要删除的 IP")
            return
        
        for card in selected:
            ip = card.ip_entry.ip
            self.config.ip_list = [e for e in self.config.ip_list if e.ip != ip]
            if ip in self.test_results:
                del self.test_results[ip]
        
        self._refresh_ip_list()
        self._save_config()
        self.status_var.set(f"已删除 {len(selected)} 个 IP")

    def _on_test_speed(self):
        """开始测速"""
        if not self.config.ip_list:
            messagebox.showinfo("提示", "没有可测试的 IP")
            return
        
        if self.is_testing:
            return
        
        self.is_testing = True
        self.test_btn.configure(state="disabled", text="测速中...")
        self.status_var.set("正在测速...")
        self.test_results.clear()
        
        def test_thread():
            def callback(current, total, result):
                self.test_results[result.ip_entry.ip] = result
                self.after(0, lambda: self._on_test_progress(current, total, result))
            
            self.speed_tester.test_all(self.config.ip_list, callback)
            self.after(0, self._on_test_complete)
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _on_test_progress(self, current, total, result):
        """测速进度更新"""
        self.status_var.set(f"测速中... {current}/{total}")
        self._refresh_ip_list()
    
    def _on_test_complete(self):
        """测速完成"""
        self.is_testing = False
        self.test_btn.configure(state="normal", text="🚀 开始测速")
        
        # 排序结果
        results = list(self.test_results.values())
        sorted_results = SpeedTester.sort_results(results)
        
        # 重新排序 IP 列表
        ip_order = {r.ip_entry.ip: i for i, r in enumerate(sorted_results)}
        self.config.ip_list.sort(key=lambda e: ip_order.get(e.ip, 999))
        
        self._refresh_ip_list()
        
        best = SpeedTester.get_best_ip(results)
        if best:
            self.status_var.set(f"测速完成，最佳 IP: {best.ip_entry.ip} ({best.latency_ms}ms)")
        else:
            self.status_var.set("测速完成，所有 IP 均不可用")
    
    def _on_apply_best_ip(self):
        """应用最佳 IP"""
        cf_domain = URLParser.extract_domain(self.cf_domain_var.get())
        if not cf_domain:
            messagebox.showerror("错误", "请先配置 CF 反代域名")
            return
        
        results = list(self.test_results.values())
        best = SpeedTester.get_best_ip(results)
        
        if not best:
            messagebox.showerror("错误", "没有可用的 IP，请先测速")
            return
        
        # 备份
        backup_path = self.hosts_manager.backup()
        if backup_path:
            self.status_var.set("已备份 hosts 文件")
        
        # 更新 hosts
        success = self.hosts_manager.update_entry(cf_domain, best.ip_entry.ip)
        
        if success:
            self.hosts_manager.flush_dns()
            self._update_hosts_status()
            self.config.selected_ip = best.ip_entry.ip
            self._save_config()
            self.status_var.set(f"已应用最佳 IP: {best.ip_entry.ip}")
            messagebox.showinfo("成功", f"已将 {cf_domain} 指向 {best.ip_entry.ip}")
        else:
            messagebox.showerror("错误", "修改 hosts 文件失败，请以管理员身份运行")
    
    def _on_clear_hosts(self):
        """清除 hosts 配置"""
        cf_domain = URLParser.extract_domain(self.cf_domain_var.get())
        if not cf_domain:
            messagebox.showinfo("提示", "请先配置 CF 反代域名")
            return
        
        if not messagebox.askyesno("确认", f"确定要删除 {cf_domain} 的 hosts 配置吗？"):
            return
        
        self.hosts_manager.backup()
        success = self.hosts_manager.remove_entry(cf_domain)
        
        if success:
            self.hosts_manager.flush_dns()
            self._update_hosts_status()
            self.config.selected_ip = None
            self._save_config()
            self.status_var.set(f"已清除 {cf_domain} 的 hosts 配置")
        else:
            messagebox.showerror("错误", "修改 hosts 文件失败，请以管理员身份运行")
    
    def _on_view_hosts(self):
        """打开 Hosts 查看器"""
        from .hosts_viewer import HostsViewer
        
        def on_viewer_close():
            self._update_hosts_status()
        
        viewer = HostsViewer(
            self,
            self.hosts_manager,
            on_close=on_viewer_close
        )
        viewer.show()
    
    def _on_theme_changed(self, value):
        """主题切换"""
        theme_map = {
            "深色": "dark",
            "浅色": "light",
            "跟随系统": "system"
        }
        mode = theme_map.get(value, "system")
        ctk.set_appearance_mode(mode)
        
        # 保存主题设置
        self.config.theme_mode = mode
        self._save_config()
        self.status_var.set(f"已切换到{value}主题")
    
    def run(self):
        """运行主循环"""
        self.mainloop()
    
    def _get_version(self) -> str:
        """获取版本号"""
        from . import __version__
        return __version__
