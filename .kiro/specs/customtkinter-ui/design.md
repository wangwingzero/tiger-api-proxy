# Design Document: CustomTkinter UI Migration

## Overview

本设计文档描述将 CF Proxy Manager 从 Tkinter 迁移到 CustomTkinter 的实现方案。采用卡片式 IP 列表、颜色编码延迟显示、深色/浅色主题支持，打造现代化的用户界面。

## Architecture

### 设计原则

1. **完全重写 GUI** - 创建新的 `gui_ctk.py`，不修改原 `gui.py`（保留作为备份）
2. **复用业务逻辑** - 继续使用现有的 models、parsers、hosts_manager、speed_tester
3. **组件化设计** - IP 卡片作为独立组件，便于复用和测试

### 文件结构

```
cf_proxy_manager/
├── gui.py           # 原 Tkinter GUI (保留)
├── gui_ctk.py       # 新 CustomTkinter GUI
├── components/      # UI 组件
│   ├── __init__.py
│   ├── ip_card.py   # IP 卡片组件
│   └── theme.py     # 主题配置
├── main.py          # 修改入口，使用新 GUI
└── ...              # 其他文件不变
```

### 依赖更新

```
# requirements.txt 新增
customtkinter>=5.2.0
```

## Components and Interfaces

### Theme 配置类

```python
# components/theme.py
class AppTheme:
    """应用主题配置"""
    
    # 延迟阈值
    LATENCY_FAST = 100      # ms
    LATENCY_MEDIUM = 300    # ms
    
    # 颜色定义
    COLORS = {
        "success": "#28a745",    # 绿色 - 快速
        "warning": "#fd7e14",    # 橙色 - 中等
        "danger": "#dc3545",     # 红色 - 慢
        "muted": "#6c757d",      # 灰色 - 待测试
        "primary": "#3b8ed0",    # 蓝色 - 主要操作
        "best_border": "#ffc107", # 金色 - 最佳IP边框
    }
    
    # 字体
    FONT_MONO = ("Consolas", 13)
    FONT_DEFAULT = ("Segoe UI", 12)
    FONT_SMALL = ("Segoe UI", 10)
    
    @staticmethod
    def get_latency_color(latency_ms: Optional[int]) -> str:
        """根据延迟返回对应颜色"""
        if latency_ms is None:
            return AppTheme.COLORS["muted"]
        if latency_ms < AppTheme.LATENCY_FAST:
            return AppTheme.COLORS["success"]
        if latency_ms < AppTheme.LATENCY_MEDIUM:
            return AppTheme.COLORS["warning"]
        return AppTheme.COLORS["danger"]
    
    @staticmethod
    def get_status_text(result) -> tuple[str, str]:
        """返回 (状态文本, 颜色)"""
        if result is None:
            return ("⏳ 待测试", AppTheme.COLORS["muted"])
        if result.success:
            return ("✓ 可用", AppTheme.COLORS["success"])
        return ("✗ 不可用", AppTheme.COLORS["danger"])
```

### IPCard 组件

```python
# components/ip_card.py
import customtkinter as ctk
from .theme import AppTheme

class IPCard(ctk.CTkFrame):
    """IP 地址卡片组件"""
    
    def __init__(self, master, ip_entry, result=None, is_best=False, 
                 on_select=None, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        
        self.ip_entry = ip_entry
        self.result = result
        self.is_best = is_best
        self.is_selected = False
        self.on_select = on_select
        
        self._create_widgets()
        self._update_appearance()
    
    def _create_widgets(self):
        """创建卡片内部组件"""
        # 主容器 - 水平布局
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
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(side="right", padx=10)
        
        # 延迟徽章
        latency_text, latency_color = self._get_latency_display()
        self.latency_badge = ctk.CTkLabel(
            status_frame,
            text=latency_text,
            fg_color=latency_color,
            corner_radius=6,
            text_color="white",
            font=AppTheme.FONT_SMALL,
            width=70
        )
        self.latency_badge.pack(side="left", padx=5)
        
        # 状态文本
        status_text, status_color = AppTheme.get_status_text(self.result)
        self.status_label = ctk.CTkLabel(
            status_frame,
            text=status_text,
            text_color=status_color,
            font=AppTheme.FONT_SMALL
        )
        self.status_label.pack(side="left", padx=5)
        
        # 最佳徽章
        if self.is_best:
            self.best_badge = ctk.CTkLabel(
                status_frame,
                text="⭐ 最佳",
                fg_color=AppTheme.COLORS["best_border"],
                corner_radius=6,
                text_color="black",
                font=AppTheme.FONT_SMALL
            )
            self.best_badge.pack(side="left", padx=5)
        
        # 绑定点击事件
        self.bind("<Button-1>", self._on_click)
        for child in self.winfo_children():
            child.bind("<Button-1>", self._on_click)
    
    def _get_latency_display(self) -> tuple[str, str]:
        """获取延迟显示文本和颜色"""
        if self.result is None:
            return ("--", AppTheme.COLORS["muted"])
        if self.result.success:
            return (f"{self.result.latency_ms}ms", 
                    AppTheme.get_latency_color(self.result.latency_ms))
        return ("--", AppTheme.COLORS["danger"])
    
    def _on_click(self, event):
        """点击事件处理"""
        self.toggle_selection()
        if self.on_select:
            self.on_select(self)
    
    def toggle_selection(self):
        """切换选中状态"""
        self.is_selected = not self.is_selected
        self._update_appearance()
    
    def _update_appearance(self):
        """更新外观"""
        if self.is_best:
            self.configure(border_width=2, border_color=AppTheme.COLORS["best_border"])
        elif self.is_selected:
            self.configure(border_width=2, border_color=AppTheme.COLORS["primary"])
        else:
            self.configure(border_width=0)
```

### 主 GUI 类

```python
# gui_ctk.py
import customtkinter as ctk
from components.ip_card import IPCard
from components.theme import AppTheme

class CFProxyManagerCTk(ctk.CTk):
    """CF Proxy Manager - CustomTkinter 版本"""
    
    def __init__(self):
        super().__init__()
        
        # 窗口配置
        self.title(f"🐯 虎哥API反代 v{self._get_version()}")
        self.geometry("700x750")
        self.minsize(600, 650)
        
        # 设置主题
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        # 初始化组件 (复用现有逻辑)
        self.config_manager = ConfigManager()
        self.speed_tester = SpeedTester(timeout=3.0)
        self.hosts_manager = HostsManager()
        self.config = self.config_manager.load()
        self.test_results = {}
        self.ip_cards = []
        
        # 创建界面
        self._create_widgets()
        self._load_config_to_ui()
```

## Data Models

无新增数据模型，复用现有 `models.py`。



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system.*

### Property 1: Latency color mapping is consistent

*For any* latency value (including None), the `get_latency_color` function SHALL return:
- Green (#28a745) for latency < 100ms
- Orange (#fd7e14) for 100ms ≤ latency < 300ms
- Red (#dc3545) for latency ≥ 300ms
- Gray (#6c757d) for None (pending/failed)

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

### Property 2: IP list to card mapping preserves count

*For any* list of N IP entries, the Scrollable_Frame SHALL create exactly N IP_Card components, one for each entry.

**Validates: Requirements 2.1**

### Property 3: IP card contains all required information

*For any* IPCard created with an ip_entry and optional result, the card SHALL display:
- The IP address from ip_entry.ip
- The port from ip_entry.port
- Latency value (or "--" if no result)
- Status text matching the result state

**Validates: Requirements 2.2**

### Property 4: Best IP identification is correct

*For any* set of test results with at least one successful result, the IP with the lowest latency SHALL be identified as "best" and receive the is_best=True flag.

**Validates: Requirements 4.1**

### Property 5: Theme preference persistence round-trip

*For any* valid theme mode ("dark", "light", "system"), saving to config and loading back SHALL return the same theme mode.

**Validates: Requirements 5.3**

### Property 6: Card selection toggle is idempotent after two clicks

*For any* IPCard, clicking twice SHALL return the card to its original selection state (toggle is self-inverse).

**Validates: Requirements 2.4**

## Error Handling

| Scenario | Handling |
|----------|----------|
| CustomTkinter not installed | Show error message, suggest `pip install customtkinter` |
| No test results | Display all cards with "待测试" status |
| All tests failed | No "best" badge displayed |
| Empty IP list | Show empty scrollable frame with placeholder text |
| Theme mode invalid | Default to "system" mode |

## Testing Strategy

### Unit Tests
- Verify `AppTheme.get_latency_color()` returns correct colors for boundary values
- Verify `AppTheme.get_status_text()` returns correct text for each state
- Verify IPCard displays correct information

### Property-Based Tests
- Use Hypothesis to generate random latency values and verify color mapping
- Generate random lists of test results and verify best IP identification
- Test theme persistence round-trip with all valid modes
- Test card selection toggle behavior

### Test Configuration
- Minimum 100 iterations per property test
- Use `hypothesis` library for property-based testing
- Tag format: **Feature: customtkinter-ui, Property N: description**
