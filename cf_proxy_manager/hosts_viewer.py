"""
CF Proxy Manager - Hosts Viewer
iOS 风格的 Hosts 查看器窗口
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, List

from .ios_widgets import (
    IOSColors, IOSFonts, IOSSizes, 
    IOSSearchEntry, IOSButton, IOSCard
)
from .hosts_manager import HostsManager
from .models import HostsEntry


# 需要过滤的本地回环 IP 地址
LOCALHOST_IPS = frozenset({"127.0.0.1", "::1", "localhost"})


def is_localhost_entry(entry: HostsEntry) -> bool:
    """
    判断是否为本地回环条目
    
    Args:
        entry: Hosts 条目
        
    Returns:
        如果是 localhost/127.0.0.1 相关条目返回 True
    """
    ip_lower = entry.ip.lower()
    domain_lower = entry.domain.lower()
    
    if ip_lower in LOCALHOST_IPS:
        return True
    
    if "localhost" in domain_lower:
        return True
    
    return False


class EntryCard(tk.Frame):
    """简洁的 Hosts 条目卡片"""
    
    def __init__(self, parent: tk.Widget, entry: HostsEntry, 
                 on_delete: Optional[Callable[[HostsEntry], None]] = None, **kwargs):
        super().__init__(parent, bg=IOSColors.CARD_BG, **kwargs)
        
        self.entry = entry
        self.on_delete = on_delete
        self._hover = False
        
        self.configure(
            highlightbackground=IOSColors.BORDER,
            highlightthickness=1,
            padx=16,
            pady=14
        )
        
        self._create_widgets()
        self._bind_events()
    
    def _create_widgets(self) -> None:
        """创建卡片内容"""
        # 左侧内容区
        content_frame = tk.Frame(self, bg=IOSColors.CARD_BG)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 域名
        self.domain_label = tk.Label(
            content_frame,
            text=self.entry.domain,
            font=("Segoe UI", 14),
            fg=IOSColors.TEXT_PRIMARY,
            bg=IOSColors.CARD_BG,
            anchor='w'
        )
        self.domain_label.pack(fill=tk.X)
        
        # IP
        self.ip_label = tk.Label(
            content_frame,
            text=self.entry.ip,
            font=("Segoe UI", 11),
            fg=IOSColors.TEXT_SECONDARY,
            bg=IOSColors.CARD_BG,
            anchor='w'
        )
        self.ip_label.pack(fill=tk.X, pady=(2, 0))
        
        # 删除按钮 - 使用文字而非 emoji
        self.delete_btn = tk.Label(
            self,
            text="删除",
            font=("Segoe UI", 11),
            fg=IOSColors.DESTRUCTIVE,
            bg=IOSColors.CARD_BG,
            cursor="hand2"
        )
        self.delete_btn.pack(side=tk.RIGHT, padx=(12, 0))
        self.delete_btn.bind('<Button-1>', self._on_delete_click)
        self.delete_btn.bind('<Enter>', lambda e: self.delete_btn.config(fg="#CC2F28"))
        self.delete_btn.bind('<Leave>', lambda e: self.delete_btn.config(fg=IOSColors.DESTRUCTIVE))
    
    def _bind_events(self) -> None:
        """绑定事件"""
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        
        for child in self.winfo_children():
            child.bind('<Enter>', self._on_enter)
            child.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, event) -> None:
        self._hover = True
        self._update_bg(IOSColors.HOVER)
    
    def _on_leave(self, event) -> None:
        x, y = self.winfo_pointerxy()
        wx, wy = self.winfo_rootx(), self.winfo_rooty()
        ww, wh = self.winfo_width(), self.winfo_height()
        
        if not (wx <= x <= wx + ww and wy <= y <= wy + wh):
            self._hover = False
            self._update_bg(IOSColors.CARD_BG)
    
    def _on_delete_click(self, event) -> str:
        if self.on_delete:
            self.on_delete(self.entry)
        return "break"
    
    def _update_bg(self, color: str) -> None:
        self.configure(bg=color)
        for child in self.winfo_children():
            try:
                child.configure(bg=color)
                for subchild in child.winfo_children():
                    try:
                        subchild.configure(bg=color)
                    except tk.TclError:
                        pass
            except tk.TclError:
                pass


class HostsViewer:
    """简洁的 Hosts 查看器窗口"""
    
    def __init__(self, parent: tk.Tk, hosts_manager: HostsManager, 
                 on_close: Optional[Callable[[], None]] = None):
        self.parent = parent
        self.hosts_manager = hosts_manager
        self.on_close = on_close
        
        self.entries: List[HostsEntry] = []
        self.cards: List[EntryCard] = []
        self.search_query = ""
        self.hide_localhost = True
        
        self._create_window()
        self._create_widgets()
        self.refresh()
    
    def _create_window(self) -> None:
        """创建窗口"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Hosts 配置")
        self.window.geometry("480x560")
        self.window.minsize(380, 400)
        self.window.configure(bg=IOSColors.BACKGROUND)
        
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        self.window.transient(self.parent)
        self.window.grab_set()
    
    def _create_widgets(self) -> None:
        """创建所有组件"""
        # 主容器
        main_frame = tk.Frame(self.window, bg=IOSColors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 顶部区域：标题 + 刷新按钮
        header_frame = tk.Frame(main_frame, bg=IOSColors.BACKGROUND)
        header_frame.pack(fill=tk.X, pady=(0, 16))
        
        title_label = tk.Label(
            header_frame,
            text="Hosts 配置",
            font=("Segoe UI", 20, "bold"),
            fg=IOSColors.TEXT_PRIMARY,
            bg=IOSColors.BACKGROUND
        )
        title_label.pack(side=tk.LEFT)
        
        # 刷新按钮 - 简洁文字
        refresh_btn = tk.Label(
            header_frame,
            text="刷新",
            font=("Segoe UI", 12),
            fg=IOSColors.ACCENT,
            bg=IOSColors.BACKGROUND,
            cursor="hand2"
        )
        refresh_btn.pack(side=tk.RIGHT)
        refresh_btn.bind('<Button-1>', lambda e: self.refresh())
        refresh_btn.bind('<Enter>', lambda e: refresh_btn.config(fg="#0056B3"))
        refresh_btn.bind('<Leave>', lambda e: refresh_btn.config(fg=IOSColors.ACCENT))
        
        # 搜索栏
        self.search_entry = IOSSearchEntry(
            main_frame,
            placeholder="搜索...",
            on_change=self._on_search
        )
        self.search_entry.pack(fill=tk.X, pady=(0, 12))
        
        # 过滤选项 - 简洁的复选框
        option_frame = tk.Frame(main_frame, bg=IOSColors.BACKGROUND)
        option_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.hide_localhost_var = tk.BooleanVar(value=True)
        self.localhost_check = tk.Checkbutton(
            option_frame,
            text="隐藏本地条目",
            variable=self.hide_localhost_var,
            command=self._on_toggle_localhost,
            font=("Segoe UI", 11),
            fg=IOSColors.TEXT_SECONDARY,
            bg=IOSColors.BACKGROUND,
            activebackground=IOSColors.BACKGROUND,
            selectcolor=IOSColors.BACKGROUND
        )
        self.localhost_check.pack(side=tk.LEFT)
        
        # 条目计数
        self.count_label = tk.Label(
            option_frame,
            text="",
            font=("Segoe UI", 11),
            fg=IOSColors.TEXT_SECONDARY,
            bg=IOSColors.BACKGROUND
        )
        self.count_label.pack(side=tk.RIGHT)
        
        # 卡片列表区域
        list_container = tk.Frame(main_frame, bg=IOSColors.BACKGROUND)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(
            list_container, 
            bg=IOSColors.BACKGROUND,
            highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            list_container, 
            orient=tk.VERTICAL, 
            command=self.canvas.yview
        )
        
        self.cards_frame = tk.Frame(self.canvas, bg=IOSColors.BACKGROUND)
        
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.cards_frame, 
            anchor='nw'
        )
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.cards_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        
        # 空状态提示
        self.empty_label = tk.Label(
            self.cards_frame,
            text="暂无配置",
            font=("Segoe UI", 13),
            fg=IOSColors.TEXT_SECONDARY,
            bg=IOSColors.BACKGROUND
        )
        
        # 底部操作栏
        action_frame = tk.Frame(main_frame, bg=IOSColors.BACKGROUND)
        action_frame.pack(fill=tk.X, pady=(16, 0))
        
        # 清空按钮 - 简洁文字
        self.clear_btn = tk.Label(
            action_frame,
            text="清空全部",
            font=("Segoe UI", 12),
            fg=IOSColors.DESTRUCTIVE,
            bg=IOSColors.BACKGROUND,
            cursor="hand2"
        )
        self.clear_btn.pack(side=tk.RIGHT)
        self.clear_btn.bind('<Button-1>', lambda e: self._on_delete_all())
        self.clear_btn.bind('<Enter>', lambda e: self.clear_btn.config(fg="#CC2F28"))
        self.clear_btn.bind('<Leave>', lambda e: self.clear_btn.config(fg=IOSColors.DESTRUCTIVE))
    
    def _on_frame_configure(self, event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def _on_canvas_configure(self, event) -> None:
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event) -> None:
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_window_close(self) -> None:
        self.canvas.unbind_all('<MouseWheel>')
        if self.on_close:
            self.on_close()
        self.window.destroy()
    
    def _on_search(self, query: str) -> None:
        self.search_query = query
        self._render_cards()
    
    def _on_toggle_localhost(self) -> None:
        self.hide_localhost = self.hide_localhost_var.get()
        self._render_cards()
    
    def _on_delete_entry(self, entry: HostsEntry) -> None:
        if not messagebox.askyesno(
            "确认",
            f"删除 {entry.domain}？",
            parent=self.window
        ):
            return
        
        success = self.hosts_manager.remove_entry(entry.domain)
        
        if success:
            self.hosts_manager.flush_dns()
            self.refresh()
        else:
            messagebox.showerror(
                "失败",
                "需要管理员权限",
                parent=self.window
            )
    
    def _on_delete_all(self) -> None:
        visible_entries = self._get_filtered_entries()
        
        if not visible_entries:
            messagebox.showinfo("提示", "没有可删除的条目", parent=self.window)
            return
        
        if not messagebox.askyesno(
            "确认",
            f"删除全部 {len(visible_entries)} 条配置？",
            parent=self.window
        ):
            return
        
        self.hosts_manager.backup()
        
        failed: List[str] = []
        for entry in visible_entries:
            if not self.hosts_manager.remove_entry(entry.domain):
                failed.append(entry.domain)
        
        self.hosts_manager.flush_dns()
        self.refresh()
        
        if failed:
            messagebox.showwarning(
                "部分失败",
                f"需要管理员权限",
                parent=self.window
            )
    
    def _get_filtered_entries(self) -> List[HostsEntry]:
        filtered = self.entries
        
        if self.hide_localhost:
            filtered = [e for e in filtered if not is_localhost_entry(e)]
        
        if self.search_query:
            filtered = [e for e in filtered if e.matches(self.search_query)]
        
        return filtered
    
    def refresh(self) -> None:
        self.entries = self.hosts_manager.get_all_entries()
        self._render_cards()
    
    def _render_cards(self) -> None:
        for card in self.cards:
            card.destroy()
        self.cards.clear()
        self.empty_label.pack_forget()
        
        filtered = self._get_filtered_entries()
        localhost_count = sum(1 for e in self.entries if is_localhost_entry(e))
        
        # 简洁的计数显示
        if self.hide_localhost and localhost_count > 0:
            self.count_label.config(text=f"{len(filtered)} 条 (+{localhost_count} 隐藏)")
        else:
            self.count_label.config(text=f"{len(filtered)} 条")
        
        if not filtered:
            self.empty_label.config(text="暂无配置" if not self.search_query else "无匹配")
            self.empty_label.pack(pady=60)
        else:
            for entry in filtered:
                card = EntryCard(
                    self.cards_frame,
                    entry=entry,
                    on_delete=self._on_delete_entry
                )
                card.pack(fill=tk.X, pady=(0, 8))
                self.cards.append(card)
    
    def show(self) -> None:
        self.window.deiconify()
        self.window.focus_set()
