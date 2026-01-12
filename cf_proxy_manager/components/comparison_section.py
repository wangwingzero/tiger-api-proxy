"""
CF Proxy Manager - Comparison Section Component
效果对比区域组件
"""
import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Optional, List, Callable

from ..models import Config, ComparisonResult, ComparisonService, DEFAULT_COMPARISON_SERVICES
from ..comparison_tester import ComparisonTester
from ..service_manager import ServiceManager
from ..parsers import URLParser
from ..logger import logger
from .theme import AppTheme
from .comparison_card import ComparisonCard


class ComparisonSection(ctk.CTkFrame):
    """效果对比区域"""
    
    def __init__(
        self,
        parent,
        config: Config,
        get_user_domain: Callable[[], str],
        get_optimized_ip: Callable[[], Optional[str]],
        on_apply: Callable[[ComparisonResult], None],
        on_save_config: Callable[[], None]
    ):
        """
        初始化效果对比区域
        
        Args:
            parent: 父组件
            config: 应用配置
            get_user_domain: 获取用户反代域名的回调
            get_optimized_ip: 获取优选 IP 的回调
            on_apply: 应用选中结果的回调
            on_save_config: 保存配置的回调
        """
        super().__init__(parent)
        
        self.config = config
        self.get_user_domain = get_user_domain
        self.get_optimized_ip = get_optimized_ip
        self.on_apply = on_apply
        self.on_save_config = on_save_config
        
        # 初始化服务管理器
        self.service_manager = ServiceManager(config.comparison_services)
        
        # 测试器
        self.tester = ComparisonTester(timeout=5.0)
        
        # 状态
        self.is_testing = False
        self.results: List[ComparisonResult] = []
        self.cards: List[ComparisonCard] = []
        self.selected_card: Optional[ComparisonCard] = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题行
        title_row = ctk.CTkFrame(self, fg_color="transparent")
        title_row.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            title_row,
            text="📊 效果对比",
            font=AppTheme.FONT_BOLD
        ).pack(side="left")
        
        # 管理按钮
        btn_frame = ctk.CTkFrame(title_row, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(
            btn_frame,
            text="管理服务",
            width=80,
            height=28,
            font=AppTheme.FONT_SMALL,
            command=self._on_manage_services
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="恢复默认",
            width=80,
            height=28,
            font=AppTheme.FONT_SMALL,
            fg_color="gray50",
            hover_color="gray40",
            command=self._on_reset_defaults
        ).pack(side="left", padx=2)
        
        # 结果展示区域（可滚动，自适应高度）
        self.results_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 初始提示
        self.placeholder = ctk.CTkLabel(
            self.results_frame,
            text="点击「开始对比」测试各反代服务的延迟",
            text_color="gray50",
            font=AppTheme.FONT_DEFAULT
        )
        self.placeholder.pack(pady=30)
        
        # 操作按钮行
        action_row = ctk.CTkFrame(self, fg_color="transparent")
        action_row.pack(fill="x", padx=15, pady=(5, 10))
        
        self.test_btn = ctk.CTkButton(
            action_row,
            text="🚀 开始对比",
            width=120,
            fg_color=AppTheme.COLORS["primary"],
            command=self._on_start_comparison
        )
        self.test_btn.pack(side="left", padx=4)
        
        # 状态显示
        self.status_var = ctk.StringVar(value="就绪")
        self.status_label = ctk.CTkLabel(
            action_row,
            textvariable=self.status_var,
            font=AppTheme.FONT_SMALL
        )
        self.status_label.pack(side="right", padx=10)
    
    def _on_start_comparison(self):
        """开始对比测试"""
        if self.is_testing:
            return
        
        user_domain = self.get_user_domain()
        if not user_domain:
            messagebox.showinfo("提示", "请先配置 CF 反代域名")
            return
        
        # 提取纯域名
        user_domain = URLParser.extract_domain(user_domain)
        if not user_domain:
            messagebox.showinfo("提示", "无效的反代域名")
            return
        
        self.is_testing = True
        self.test_btn.configure(state="disabled", text="测试中...")
        self.status_var.set("正在测试...")
        
        # 清空结果
        self._clear_results()
        
        # 获取优选 IP
        optimized_ip = self.get_optimized_ip()
        
        # 获取对比服务
        services = self.service_manager.get_all()
        
        def test_thread():
            def callback(current, total, result):
                self.after(0, lambda: self._on_test_progress(current, total, result))
            
            results = self.tester.run_comparison(
                user_domain=user_domain,
                optimized_ip=optimized_ip,
                services=services,
                callback=callback
            )
            self.after(0, lambda: self._on_test_complete(results))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _on_test_progress(self, current: int, total: int, result: ComparisonResult):
        """测试进度更新"""
        self.status_var.set(f"测试中... {current}/{total}")
    
    def _on_test_complete(self, results: List[ComparisonResult]):
        """测试完成"""
        self.is_testing = False
        self.test_btn.configure(state="normal", text="🚀 开始对比")
        self.results = results
        
        # 显示结果
        self._display_results(results)
        
        # 更新状态
        successful = sum(1 for r in results if r.success)
        self.status_var.set(f"完成: {successful}/{len(results)} 可用")
    
    def _clear_results(self):
        """清空结果显示"""
        for card in self.cards:
            card.destroy()
        self.cards.clear()
        self.selected_card = None
        
        # 显示占位符
        if hasattr(self, 'placeholder') and self.placeholder.winfo_exists():
            self.placeholder.pack(pady=30)
    
    def _display_results(self, results: List[ComparisonResult]):
        """显示对比结果"""
        logger.info(f"显示对比结果: {len(results)} 个")
        
        # 隐藏占位符
        if hasattr(self, 'placeholder') and self.placeholder.winfo_exists():
            self.placeholder.pack_forget()
        
        # 清空现有卡片
        for card in self.cards:
            card.destroy()
        self.cards.clear()
        
        # 找出最佳结果
        best_result = self.tester.get_best_result(results)
        logger.debug(f"最佳结果: {best_result.service.name if best_result else 'None'}")
        
        # 创建卡片
        for result in results:
            is_best = (best_result is not None and 
                      result.service.url == best_result.service.url and
                      result.latency_ms == best_result.latency_ms)
            
            logger.debug(f"创建卡片: {result.service.name}, latency={result.latency_ms}, packet_loss={getattr(result, 'packet_loss', 'N/A')}")
            
            card = ComparisonCard(
                self.results_frame,
                result=result,
                is_best=is_best,
                on_select=self._on_card_select
            )
            card.pack(fill="x", pady=3, padx=5)
            self.cards.append(card)
        
        logger.info(f"创建了 {len(self.cards)} 个卡片")
    
    def _on_card_select(self, card: ComparisonCard):
        """卡片选中回调 - 点击即应用"""
        logger.info(f"卡片点击: {card.result.service.name}")
        
        # 取消其他卡片的选中状态
        for c in self.cards:
            if c != card:
                c.set_selected(False)
        
        # 确保当前卡片选中
        card.set_selected(True)
        self.selected_card = card
        
        # 直接应用结果
        result = card.result
        logger.info(f"直接应用: {result.service.name}, is_optimized={result.is_optimized}")
        self.on_apply(result)
    
    def _on_manage_services(self):
        """管理对比服务"""
        dialog = ServiceManagerDialog(
            self,
            self.service_manager,
            on_save=self._on_services_changed
        )
        dialog.show()
    
    def _on_services_changed(self):
        """服务列表变更回调"""
        # 更新配置
        self.config.comparison_services = self.service_manager.get_all()
        self.on_save_config()
        self.status_var.set("服务列表已更新")
    
    def _on_reset_defaults(self):
        """恢复默认服务"""
        if not messagebox.askyesno("确认", "确定要恢复默认对比服务列表吗？"):
            return
        
        self.service_manager.reset_to_defaults()
        self.config.comparison_services = self.service_manager.get_all()
        self.on_save_config()
        self.status_var.set("已恢复默认服务")


class ServiceManagerDialog(ctk.CTkToplevel):
    """服务管理对话框"""
    
    def __init__(
        self,
        parent,
        service_manager: ServiceManager,
        on_save: Callable[[], None]
    ):
        super().__init__(parent)
        
        self.service_manager = service_manager
        self.on_save = on_save
        
        self.title("管理对比服务")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # 模态
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self._refresh_list()
    
    def _create_widgets(self):
        """创建界面"""
        # 服务列表
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            list_frame,
            text="对比服务列表",
            font=AppTheme.FONT_BOLD
        ).pack(anchor="w", pady=(0, 5))
        
        self.service_listbox = ctk.CTkScrollableFrame(list_frame, height=200)
        self.service_listbox.pack(fill="both", expand=True)
        
        # 添加服务
        add_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(add_frame, text="名称:", font=AppTheme.FONT_SMALL).pack(side="left")
        self.name_entry = ctk.CTkEntry(add_frame, width=100)
        self.name_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(add_frame, text="URL:", font=AppTheme.FONT_SMALL).pack(side="left")
        self.url_entry = ctk.CTkEntry(add_frame, width=200)
        self.url_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            add_frame,
            text="添加",
            width=60,
            command=self._on_add
        ).pack(side="left", padx=5)
        
        # 底部按钮
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkButton(
            btn_frame,
            text="关闭",
            width=80,
            command=self._on_close
        ).pack(side="right")
    
    def _refresh_list(self):
        """刷新服务列表"""
        # 清空
        for widget in self.service_listbox.winfo_children():
            widget.destroy()
        
        # 添加服务项
        for service in self.service_manager.get_all():
            row = ctk.CTkFrame(self.service_listbox, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            # 服务信息
            info = f"{service.name} - {service.url[:40]}..."
            ctk.CTkLabel(
                row,
                text=info,
                font=AppTheme.FONT_SMALL,
                anchor="w"
            ).pack(side="left", fill="x", expand=True)
            
            # 删除按钮
            ctk.CTkButton(
                row,
                text="删除",
                width=50,
                height=24,
                fg_color="gray50",
                hover_color="gray40",
                command=lambda url=service.url: self._on_delete(url)
            ).pack(side="right")
    
    def _on_add(self):
        """添加服务"""
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        
        if not name or not url:
            messagebox.showerror("错误", "请输入名称和 URL")
            return
        
        if not url.startswith("https://"):
            url = "https://" + url
        
        if self.service_manager.add_service(name, url):
            self.name_entry.delete(0, "end")
            self.url_entry.delete(0, "end")
            self._refresh_list()
            self.on_save()
        else:
            messagebox.showerror("错误", "无效的 URL 或服务已存在")
    
    def _on_delete(self, url: str):
        """删除服务"""
        self.service_manager.remove_service(url)
        self._refresh_list()
        self.on_save()
    
    def _on_close(self):
        """关闭对话框"""
        self.destroy()
    
    def show(self):
        """显示对话框"""
        self.wait_window()
