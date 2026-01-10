"""
CF Proxy Manager - iOS Style Widgets
iOS 风格 UI 组件
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class IOSColors:
    """iOS 风格颜色常量"""
    BACKGROUND = "#F5F5F7"      # 浅灰背景
    CARD_BG = "#FFFFFF"         # 白色卡片
    ACCENT = "#007AFF"          # iOS 蓝色
    DESTRUCTIVE = "#FF3B30"     # iOS 红色
    SUCCESS = "#34C759"         # iOS 绿色
    WARNING = "#FF9500"         # iOS 橙色
    TEXT_PRIMARY = "#1D1D1F"    # 主文字
    TEXT_SECONDARY = "#86868B"  # 次要文字
    BORDER = "#E5E5EA"          # 边框色
    HOVER = "#F0F0F5"           # 悬停色
    SELECTED = "#E8F4FD"        # 选中色


class IOSFonts:
    """iOS 风格字体"""
    FAMILY = "Segoe UI"
    TITLE = (FAMILY, 16, "bold")
    BODY = (FAMILY, 14)
    CAPTION = (FAMILY, 12)
    BUTTON = (FAMILY, 14)


class IOSSizes:
    """iOS 风格尺寸"""
    CORNER_RADIUS = 10
    CARD_PADDING = 16
    CARD_SPACING = 8
    SEARCH_HEIGHT = 36
    BUTTON_HEIGHT = 44
    BUTTON_PADDING = 12


class RoundedFrame(tk.Canvas):
    """圆角边框 Frame"""
    
    def __init__(self, parent, bg_color: str = IOSColors.CARD_BG, 
                 border_color: str = IOSColors.BORDER,
                 corner_radius: int = IOSSizes.CORNER_RADIUS,
                 **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.bg_color = bg_color
        self.border_color = border_color
        self.corner_radius = corner_radius
        self.configure(bg=parent.cget('bg') if hasattr(parent, 'cget') else IOSColors.BACKGROUND)
        
        # 内部 Frame 用于放置子组件
        self.inner_frame = tk.Frame(self, bg=bg_color)
        
        self.bind('<Configure>', self._on_resize)
    
    def _on_resize(self, event=None):
        """重绘圆角矩形"""
        self.delete('rounded_rect')
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width > 1 and height > 1:
            self._draw_rounded_rect(0, 0, width, height)
            # 更新内部 Frame 位置
            self.create_window(
                self.corner_radius // 2, 
                self.corner_radius // 2,
                window=self.inner_frame,
                anchor='nw',
                width=width - self.corner_radius,
                height=height - self.corner_radius,
                tags='inner_frame'
            )
    
    def _draw_rounded_rect(self, x1, y1, x2, y2):
        """绘制圆角矩形"""
        r = self.corner_radius
        
        # 绘制填充的圆角矩形
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        
        self.create_polygon(
            points, 
            fill=self.bg_color, 
            outline=self.border_color,
            smooth=True,
            tags='rounded_rect'
        )


class IOSButton(tk.Canvas):
    """iOS 风格按钮"""
    
    def __init__(self, parent, text: str, command: Callable = None,
                 style: str = "default", width: int = 100, height: int = IOSSizes.BUTTON_HEIGHT,
                 **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        
        self.text = text
        self.command = command
        self.style = style
        self.width = width
        self.height = height
        self._pressed = False
        self._hover = False
        
        # 根据样式设置颜色
        if style == "primary":
            self.bg_color = IOSColors.ACCENT
            self.text_color = "#FFFFFF"
            self.hover_color = "#0056B3"
        elif style == "destructive":
            self.bg_color = IOSColors.DESTRUCTIVE
            self.text_color = "#FFFFFF"
            self.hover_color = "#CC2F28"
        else:  # default
            self.bg_color = IOSColors.CARD_BG
            self.text_color = IOSColors.ACCENT
            self.hover_color = IOSColors.HOVER
        
        self.configure(bg=parent.cget('bg') if hasattr(parent, 'cget') else IOSColors.BACKGROUND)
        
        # 绑定事件
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        
        self._draw()
    
    def _draw(self):
        """绘制按钮"""
        self.delete('all')
        
        # 确定当前背景色
        if self._pressed:
            bg = self.hover_color
        elif self._hover:
            bg = self.hover_color if self.style == "default" else self.bg_color
        else:
            bg = self.bg_color
        
        # 绘制圆角矩形背景
        r = IOSSizes.CORNER_RADIUS
        self.create_oval(0, 0, r*2, r*2, fill=bg, outline=IOSColors.BORDER if self.style == "default" else "")
        self.create_oval(self.width-r*2, 0, self.width, r*2, fill=bg, outline=IOSColors.BORDER if self.style == "default" else "")
        self.create_oval(0, self.height-r*2, r*2, self.height, fill=bg, outline=IOSColors.BORDER if self.style == "default" else "")
        self.create_oval(self.width-r*2, self.height-r*2, self.width, self.height, fill=bg, outline=IOSColors.BORDER if self.style == "default" else "")
        self.create_rectangle(r, 0, self.width-r, self.height, fill=bg, outline="")
        self.create_rectangle(0, r, self.width, self.height-r, fill=bg, outline="")
        
        # 绘制边框 (仅 default 样式)
        if self.style == "default":
            self.create_arc(0, 0, r*2, r*2, start=90, extent=90, style='arc', outline=IOSColors.BORDER)
            self.create_arc(self.width-r*2, 0, self.width, r*2, start=0, extent=90, style='arc', outline=IOSColors.BORDER)
            self.create_arc(0, self.height-r*2, r*2, self.height, start=180, extent=90, style='arc', outline=IOSColors.BORDER)
            self.create_arc(self.width-r*2, self.height-r*2, self.width, self.height, start=270, extent=90, style='arc', outline=IOSColors.BORDER)
            self.create_line(r, 0, self.width-r, 0, fill=IOSColors.BORDER)
            self.create_line(r, self.height, self.width-r, self.height, fill=IOSColors.BORDER)
            self.create_line(0, r, 0, self.height-r, fill=IOSColors.BORDER)
            self.create_line(self.width, r, self.width, self.height-r, fill=IOSColors.BORDER)
        
        # 绘制文字
        self.create_text(
            self.width // 2, self.height // 2,
            text=self.text,
            fill=self.text_color,
            font=IOSFonts.BUTTON
        )
    
    def _on_enter(self, event):
        self._hover = True
        self._draw()
    
    def _on_leave(self, event):
        self._hover = False
        self._pressed = False
        self._draw()
    
    def _on_press(self, event):
        self._pressed = True
        self._draw()
    
    def _on_release(self, event):
        self._pressed = False
        self._draw()
        if self.command and self._hover:
            self.command()


class IOSSearchEntry(tk.Frame):
    """iOS 风格搜索框"""
    
    def __init__(self, parent, placeholder: str = "搜索...", 
                 on_change: Callable = None, **kwargs):
        super().__init__(parent, bg=IOSColors.BACKGROUND, **kwargs)
        
        self.placeholder = placeholder
        self.on_change = on_change
        self._has_focus = False
        
        # 搜索框容器
        self.container = tk.Frame(self, bg=IOSColors.CARD_BG, padx=12, pady=8)
        self.container.pack(fill=tk.X, padx=2, pady=2)
        
        # 搜索图标
        self.icon_label = tk.Label(
            self.container, 
            text="🔍", 
            bg=IOSColors.CARD_BG,
            fg=IOSColors.TEXT_SECONDARY,
            font=IOSFonts.BODY
        )
        self.icon_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # 输入框
        self.var = tk.StringVar()
        self.entry = tk.Entry(
            self.container,
            textvariable=self.var,
            font=IOSFonts.BODY,
            bg=IOSColors.CARD_BG,
            fg=IOSColors.TEXT_PRIMARY,
            relief='flat',
            insertbackground=IOSColors.ACCENT
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 清除按钮
        self.clear_btn = tk.Label(
            self.container,
            text="✕",
            bg=IOSColors.CARD_BG,
            fg=IOSColors.TEXT_SECONDARY,
            font=IOSFonts.CAPTION,
            cursor="hand2"
        )
        self.clear_btn.bind('<Button-1>', self._on_clear)
        
        # 绑定事件
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.var.trace_add('write', self._on_text_change)
        
        # 显示占位符
        self._show_placeholder()
    
    def _show_placeholder(self):
        """显示占位符"""
        if not self.var.get() and not self._has_focus:
            self.entry.config(fg=IOSColors.TEXT_SECONDARY)
            self.var.set(self.placeholder)
    
    def _hide_placeholder(self):
        """隐藏占位符"""
        if self.var.get() == self.placeholder:
            self.var.set("")
        self.entry.config(fg=IOSColors.TEXT_PRIMARY)
    
    def _on_focus_in(self, event):
        self._has_focus = True
        self._hide_placeholder()
    
    def _on_focus_out(self, event):
        self._has_focus = False
        if not self.var.get():
            self._show_placeholder()
    
    def _on_text_change(self, *args):
        """文本变化回调"""
        text = self.get()
        
        # 显示/隐藏清除按钮
        if text:
            self.clear_btn.pack(side=tk.RIGHT, padx=(8, 0))
        else:
            self.clear_btn.pack_forget()
        
        # 调用外部回调
        if self.on_change and self.var.get() != self.placeholder:
            self.on_change(text)
    
    def _on_clear(self, event):
        """清除输入"""
        self.var.set("")
        self.entry.focus_set()
        if self.on_change:
            self.on_change("")
    
    def get(self) -> str:
        """获取输入值"""
        value = self.var.get()
        return "" if value == self.placeholder else value
    
    def set(self, value: str):
        """设置输入值"""
        self._hide_placeholder()
        self.var.set(value)


class IOSCard(tk.Frame):
    """iOS 风格卡片"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=IOSColors.CARD_BG, **kwargs)
        
        self._hover = False
        self._selected = False
        
        # 配置边框效果
        self.configure(
            highlightbackground=IOSColors.BORDER,
            highlightthickness=1,
            padx=IOSSizes.CARD_PADDING,
            pady=IOSSizes.CARD_PADDING
        )
        
        # 绑定悬停事件
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, event):
        if not self._selected:
            self._hover = True
            self.configure(bg=IOSColors.HOVER)
            self._update_children_bg(IOSColors.HOVER)
    
    def _on_leave(self, event):
        if not self._selected:
            self._hover = False
            self.configure(bg=IOSColors.CARD_BG)
            self._update_children_bg(IOSColors.CARD_BG)
    
    def _update_children_bg(self, color: str) -> None:
        """更新所有子组件背景色"""
        for child in self.winfo_children():
            try:
                child.configure(bg=color)
            except tk.TclError:
                pass
    
    def select(self) -> None:
        """选中状态"""
        self._selected = True
        self.configure(bg=IOSColors.SELECTED)
        self._update_children_bg(IOSColors.SELECTED)
    
    def deselect(self) -> None:
        """取消选中"""
        self._selected = False
        self.configure(bg=IOSColors.CARD_BG)
        self._update_children_bg(IOSColors.CARD_BG)


class IOSToggle(tk.Canvas):
    """iOS 风格开关组件"""
    
    # 开关尺寸常量
    WIDTH = 51
    HEIGHT = 31
    PADDING = 2
    
    def __init__(self, parent, text: str = "", on_change: Optional[Callable[[bool], None]] = None,
                 initial_state: bool = False, **kwargs):
        """
        初始化 iOS 风格开关
        
        Args:
            parent: 父组件
            text: 开关标签文字
            on_change: 状态变化回调函数
            initial_state: 初始状态
        """
        # 创建容器 Frame
        self.container = tk.Frame(parent, bg=IOSColors.BACKGROUND)
        
        # 标签
        if text:
            self.label = tk.Label(
                self.container,
                text=text,
                font=IOSFonts.BODY,
                fg=IOSColors.TEXT_PRIMARY,
                bg=IOSColors.BACKGROUND
            )
            self.label.pack(side=tk.LEFT, padx=(0, 10))
        
        # 开关 Canvas
        super().__init__(
            self.container, 
            width=self.WIDTH, 
            height=self.HEIGHT, 
            highlightthickness=0,
            bg=IOSColors.BACKGROUND,
            **kwargs
        )
        self.pack(side=tk.LEFT)
        
        self._state = initial_state
        self._on_change = on_change
        
        # 绑定点击事件
        self.bind('<Button-1>', self._on_click)
        
        self._draw()
    
    def _draw(self) -> None:
        """绘制开关"""
        self.delete('all')
        
        # 背景颜色
        bg_color = IOSColors.SUCCESS if self._state else IOSColors.BORDER
        
        # 绘制圆角背景
        r = self.HEIGHT // 2
        self.create_oval(0, 0, self.HEIGHT, self.HEIGHT, fill=bg_color, outline="")
        self.create_oval(self.WIDTH - self.HEIGHT, 0, self.WIDTH, self.HEIGHT, fill=bg_color, outline="")
        self.create_rectangle(r, 0, self.WIDTH - r, self.HEIGHT, fill=bg_color, outline="")
        
        # 绘制圆形滑块
        knob_r = (self.HEIGHT - self.PADDING * 2) // 2
        if self._state:
            knob_x = self.WIDTH - self.PADDING - knob_r
        else:
            knob_x = self.PADDING + knob_r
        knob_y = self.HEIGHT // 2
        
        self.create_oval(
            knob_x - knob_r, knob_y - knob_r,
            knob_x + knob_r, knob_y + knob_r,
            fill="#FFFFFF", outline=""
        )
    
    def _on_click(self, event) -> None:
        """点击切换状态"""
        self._state = not self._state
        self._draw()
        if self._on_change:
            self._on_change(self._state)
    
    def get(self) -> bool:
        """获取当前状态"""
        return self._state
    
    def set(self, state: bool) -> None:
        """设置状态"""
        if self._state != state:
            self._state = state
            self._draw()
    
    def pack(self, **kwargs) -> None:
        """重写 pack 方法，使容器可以正确布局"""
        self.container.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """重写 grid 方法，使容器可以正确布局"""
        self.container.grid(**kwargs)
    
    def place(self, **kwargs) -> None:
        """重写 place 方法，使容器可以正确布局"""
        self.container.place(**kwargs)
