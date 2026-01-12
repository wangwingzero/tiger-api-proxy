"""
CF Proxy Manager - IP Card Component
IP 地址卡片组件
"""
import customtkinter as ctk
from typing import Optional, Callable, Any

from .theme import AppTheme


class IPCard(ctk.CTkFrame):
    """
    IP 地址卡片组件
    
    显示单个 IP 的信息，包括：
    - IP 地址和端口
    - 延迟徽章（颜色编码）
    - 状态文本
    - 最佳 IP 徽章（可选）
    """
    
    # 最小高度
    MIN_HEIGHT = 50
    
    def __init__(
        self, 
        master: Any,
        ip_entry: Any,
        result: Optional[Any] = None,
        is_best: bool = False,
        on_select: Optional[Callable[["IPCard"], None]] = None,
        **kwargs
    ):
        """
        初始化 IP 卡片
        
        Args:
            master: 父容器
            ip_entry: IPEntry 对象，包含 ip 和 port 属性
            result: TestResult 对象或 None
            is_best: 是否为最佳 IP
            on_select: 选中回调函数
        """
        super().__init__(master, corner_radius=10, **kwargs)
        
        self.ip_entry = ip_entry
        self.result = result
        self.is_best = is_best
        self.is_selected = False
        self.on_select = on_select
        
        # 设置最小高度
        self.configure(height=self.MIN_HEIGHT)
        
        self._create_widgets()
        self._update_appearance()
    
    def _create_widgets(self):
        """创建卡片内部组件"""
        # 设置卡片背景色（支持深色/浅色模式）
        self.configure(fg_color=("gray95", "gray20"))
        
        # IP 地址标签 (左侧)
        ip_text = f"{self.ip_entry.ip}:{self.ip_entry.port}"
        self.ip_label = ctk.CTkLabel(
            self,
            text=ip_text,
            font=AppTheme.FONT_MONO,
            anchor="w"
        )
        self.ip_label.pack(side="left", padx=15, pady=12)
        
        # 状态区域 (右侧)
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(side="right", padx=10, pady=8)
        
        # 最佳徽章（如果是最佳 IP）
        if self.is_best:
            self.best_badge = ctk.CTkLabel(
                self.status_frame,
                text="⭐ 最佳",
                fg_color=AppTheme.COLORS["best_border"],
                corner_radius=6,
                text_color="black",
                font=AppTheme.FONT_SMALL,
                padx=8,
                pady=2
            )
            self.best_badge.pack(side="right", padx=5)
        
        # 状态文本
        status_text, status_color = AppTheme.get_status_text(self.result)
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text=status_text,
            text_color=status_color,
            font=AppTheme.FONT_SMALL
        )
        self.status_label.pack(side="right", padx=5)
        
        # 延迟徽章
        latency_text, latency_color = AppTheme.get_latency_display(self.result)
        self.latency_badge = ctk.CTkLabel(
            self.status_frame,
            text=latency_text,
            fg_color=latency_color,
            corner_radius=6,
            text_color="white",
            font=AppTheme.FONT_SMALL,
            width=70,
            padx=8,
            pady=2
        )
        self.latency_badge.pack(side="right", padx=5)
        
        # 绑定点击事件到所有子组件
        self._bind_click_events()
    
    def _bind_click_events(self):
        """绑定点击事件到卡片及其所有子组件"""
        self.bind("<Button-1>", self._on_click)
        self.bind("<Shift-Button-1>", self._on_shift_click)
        for child in self.winfo_children():
            child.bind("<Button-1>", self._on_click)
            child.bind("<Shift-Button-1>", self._on_shift_click)
            # 递归绑定子组件的子组件
            for grandchild in child.winfo_children():
                grandchild.bind("<Button-1>", self._on_click)
                grandchild.bind("<Shift-Button-1>", self._on_shift_click)
    
    def _on_click(self, event):
        """点击事件处理"""
        self.toggle_selection()
        if self.on_select:
            self.on_select(self, shift_held=False)
    
    def _on_shift_click(self, event):
        """Shift+点击事件处理"""
        self.set_selected(True)
        if self.on_select:
            self.on_select(self, shift_held=True)
    
    def toggle_selection(self):
        """切换选中状态"""
        self.is_selected = not self.is_selected
        self._update_appearance()
    
    def set_selected(self, selected: bool):
        """设置选中状态"""
        self.is_selected = selected
        self._update_appearance()
    
    def _update_appearance(self):
        """更新卡片外观"""
        if self.is_selected:
            # 选中状态：蓝色边框 + 浅蓝背景（优先级最高）
            self.configure(
                fg_color=("#cce5ff", "#1a3a5c"),  # 浅蓝/深蓝背景
                border_width=3,
                border_color=AppTheme.COLORS["primary"]
            )
        elif self.is_best:
            # 最佳 IP：金色边框
            self.configure(
                fg_color=("gray95", "gray20"),
                border_width=2, 
                border_color=AppTheme.COLORS["best_border"]
            )
        else:
            # 默认：无边框
            self.configure(
                fg_color=("gray95", "gray20"),
                border_width=0
            )
    
    def update_result(self, result: Optional[Any], is_best: bool = False):
        """
        更新测试结果
        
        Args:
            result: 新的 TestResult 对象
            is_best: 是否为最佳 IP
        """
        self.result = result
        self.is_best = is_best
        
        # 更新延迟徽章
        latency_text, latency_color = AppTheme.get_latency_display(result)
        self.latency_badge.configure(text=latency_text, fg_color=latency_color)
        
        # 更新状态文本
        status_text, status_color = AppTheme.get_status_text(result)
        self.status_label.configure(text=status_text, text_color=status_color)
        
        # 更新最佳徽章
        if is_best and not hasattr(self, 'best_badge'):
            self.best_badge = ctk.CTkLabel(
                self.status_frame,
                text="⭐ 最佳",
                fg_color=AppTheme.COLORS["best_border"],
                corner_radius=6,
                text_color="black",
                font=AppTheme.FONT_SMALL,
                padx=8,
                pady=2
            )
            self.best_badge.pack(side="right", padx=5)
        elif not is_best and hasattr(self, 'best_badge'):
            self.best_badge.destroy()
            delattr(self, 'best_badge')
        
        self._update_appearance()
    
    def get_ip_text(self) -> str:
        """获取 IP 地址文本"""
        return f"{self.ip_entry.ip}:{self.ip_entry.port}"
    
    def get_latency_text(self) -> str:
        """获取延迟文本"""
        return self.latency_badge.cget("text")
    
    def get_status_text(self) -> str:
        """获取状态文本"""
        return self.status_label.cget("text")
