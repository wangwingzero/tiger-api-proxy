"""
CF Proxy Manager - Comparison Card Component
对比结果卡片组件
"""
import customtkinter as ctk
from typing import Optional, Callable

from ..models import ComparisonResult
from ..logger import logger
from .theme import AppTheme


class ComparisonCard(ctk.CTkFrame):
    """对比结果卡片"""
    
    # 延迟等级颜色
    LEVEL_COLORS = {
        'fast': "#28a745",    # 绿色 < 200ms
        'medium': "#fd7e14",  # 橙色 200-500ms
        'slow': "#dc3545",    # 红色 > 500ms
        'failed': "#6c757d",  # 灰色 失败
    }
    
    # 丢包率颜色
    PACKET_LOSS_COLORS = {
        'stable': "#28a745",    # 绿色 < 10%
        'unstable': "#fd7e14",  # 橙色 10-30%
        'bad': "#dc3545",       # 红色 > 30%
    }
    
    def __init__(
        self,
        parent,
        result: ComparisonResult,
        is_best: bool = False,
        on_select: Optional[Callable[["ComparisonCard"], None]] = None
    ):
        """
        初始化对比结果卡片
        
        Args:
            parent: 父组件
            result: 对比测试结果
            is_best: 是否为最佳选项
            on_select: 选中回调
        """
        super().__init__(parent, corner_radius=8)
        
        self.result = result
        self.is_best = is_best
        self.on_select = on_select
        self.is_selected = False
        
        logger.debug(f"创建 ComparisonCard: {result.service.name}, on_select={on_select is not None}")
        
        # 设置边框颜色
        if is_best:
            self.configure(border_width=2, border_color=AppTheme.COLORS["best_border"])
        
        self._create_widgets()
        self._bind_click_events()
    
    def _create_widgets(self):
        """创建卡片内容"""
        # 主容器
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)
        
        # 左侧：服务信息
        left_frame = ctk.CTkFrame(content, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True)
        
        # 服务名称行
        name_row = ctk.CTkFrame(left_frame, fg_color="transparent")
        name_row.pack(fill="x")
        
        # 最佳标签
        if self.is_best:
            best_label = ctk.CTkLabel(
                name_row,
                text="🏆 最佳",
                font=AppTheme.FONT_SMALL,
                text_color=AppTheme.COLORS["best_border"]
            )
            best_label.pack(side="left", padx=(0, 5))
        
        # 服务名称
        name_label = ctk.CTkLabel(
            name_row,
            text=self.result.service.name,
            font=AppTheme.FONT_BOLD
        )
        name_label.pack(side="left")
        
        # 基准/优选标签
        if self.result.is_baseline:
            tag_label = ctk.CTkLabel(
                name_row,
                text="[基准]",
                font=AppTheme.FONT_SMALL,
                text_color=AppTheme.COLORS["primary"]
            )
            tag_label.pack(side="left", padx=5)
        elif self.result.is_optimized:
            tag_label = ctk.CTkLabel(
                name_row,
                text="[优选IP]",
                font=AppTheme.FONT_SMALL,
                text_color=AppTheme.COLORS["success"]
            )
            tag_label.pack(side="left", padx=5)
        
        # 描述
        if self.result.service.description:
            desc_label = ctk.CTkLabel(
                left_frame,
                text=self.result.service.description,
                font=AppTheme.FONT_SMALL,
                text_color="gray50"
            )
            desc_label.pack(anchor="w")
        
        # 右侧：延迟和提升
        right_frame = ctk.CTkFrame(content, fg_color="transparent")
        right_frame.pack(side="right")
        
        # 延迟显示
        latency_color = self.LEVEL_COLORS.get(self.result.latency_level, "gray50")
        
        if self.result.success and self.result.latency_ms is not None:
            latency_text = f"{int(self.result.latency_ms)}ms"
        else:
            latency_text = "失败"
        
        latency_label = ctk.CTkLabel(
            right_frame,
            text=latency_text,
            font=("Consolas", 16, "bold"),
            text_color=latency_color
        )
        latency_label.pack(anchor="e")
        
        # 丢包率显示
        packet_loss = getattr(self.result, 'packet_loss', 0.0)
        if packet_loss < 10:
            loss_color = self.PACKET_LOSS_COLORS['stable']
        elif packet_loss < 30:
            loss_color = self.PACKET_LOSS_COLORS['unstable']
        else:
            loss_color = self.PACKET_LOSS_COLORS['bad']
        
        loss_text = f"丢包 {packet_loss:.0f}%"
        loss_label = ctk.CTkLabel(
            right_frame,
            text=loss_text,
            font=AppTheme.FONT_SMALL,
            text_color=loss_color
        )
        loss_label.pack(anchor="e")
        
        # 提升百分比
        if self.result.improvement_pct is not None:
            if self.result.improvement_pct > 0:
                improvement_text = f"↑ {self.result.improvement_pct:.0f}%"
                improvement_color = AppTheme.COLORS["success"]
            elif self.result.improvement_pct < 0:
                improvement_text = f"↓ {abs(self.result.improvement_pct):.0f}%"
                improvement_color = AppTheme.COLORS["danger"]
            else:
                improvement_text = "= 0%"
                improvement_color = "gray50"
            
            improvement_label = ctk.CTkLabel(
                right_frame,
                text=improvement_text,
                font=AppTheme.FONT_SMALL,
                text_color=improvement_color
            )
            improvement_label.pack(anchor="e")
        
        # 错误信息
        if not self.result.success and self.result.error_message:
            error_label = ctk.CTkLabel(
                right_frame,
                text=self.result.error_message[:20],
                font=AppTheme.FONT_SMALL,
                text_color=AppTheme.COLORS["danger"]
            )
            error_label.pack(anchor="e")
    
    def _bind_click_events(self):
        """递归绑定点击事件到所有子组件"""
        self.bind("<Button-1>", self._on_click)
        self.bind("<Double-Button-1>", self._on_double_click)
        self._bind_children_click(self)
    
    def _bind_children_click(self, widget):
        """递归绑定子组件点击事件"""
        for child in widget.winfo_children():
            child.bind("<Button-1>", self._on_click)
            child.bind("<Double-Button-1>", self._on_double_click)
            self._bind_children_click(child)
    
    def _on_click(self, event=None):
        """单击事件处理 - 选中卡片"""
        logger.info(f"ComparisonCard 单击: {self.result.service.name}")
        self.set_selected(True)
    
    def _on_double_click(self, event=None):
        """双击事件处理 - 选中并触发应用回调"""
        logger.info(f"ComparisonCard 双击: {self.result.service.name}")
        self.set_selected(True)
        if self.on_select:
            logger.debug(f"调用 on_select 回调")
            self.on_select(self)
        else:
            logger.warning(f"on_select 回调未设置")
    
    def toggle_selection(self):
        """切换选中状态"""
        self.is_selected = not self.is_selected
        self._update_selection_style()
    
    def set_selected(self, selected: bool):
        """设置选中状态"""
        self.is_selected = selected
        self._update_selection_style()
    
    def _update_selection_style(self):
        """更新选中样式"""
        if self.is_selected:
            # 选中状态：蓝色边框 + 深色背景
            self.configure(
                fg_color=("#cce5ff", "#1a3a5c"),  # 浅蓝/深蓝背景
                border_width=3,
                border_color=AppTheme.COLORS["primary"]  # 蓝色边框
            )
        else:
            # 未选中状态
            if self.is_best:
                # 最佳项：黄色边框
                self.configure(
                    fg_color=("gray95", "gray17"),
                    border_width=2,
                    border_color=AppTheme.COLORS["best_border"]
                )
            else:
                # 普通项：无边框（使用与背景相同的颜色）
                self.configure(
                    fg_color=("gray95", "gray17"),
                    border_width=1,
                    border_color=("gray95", "gray17")
                )
