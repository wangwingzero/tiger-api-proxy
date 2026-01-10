# Design Document: Hosts Viewer

## Overview

Hosts Viewer 是一个独立的 Tkinter 窗口组件，采用 iOS 风格设计，用于展示和管理 Windows hosts 文件中的所有条目。该组件复用现有的 `HostsManager` 类进行文件操作，并通过自定义 Canvas 绘制实现圆角卡片等 iOS 风格 UI 元素。

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Hosts Viewer Window                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Search Bar (iOS Style)                  │   │
│  │  🔍 [Search domain or IP...              ] [Clear]   │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Entry Cards List                     │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  📍 betterclau.de                    [🗑️]   │    │   │
│  │  │     104.21.52.82                             │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  📍 proxy.example.com                [🗑️]   │    │   │
│  │  │     103.21.244.78                            │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                      ...                             │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Action Bar                              │   │
│  │  [🔄 刷新]                          [🗑️ 删除全部]    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. HostsViewer (主窗口类)

```python
class HostsViewer:
    """iOS 风格的 Hosts 查看器窗口"""
    
    def __init__(self, parent: tk.Tk, hosts_manager: HostsManager, on_close: Callable = None):
        """
        初始化 Hosts 查看器
        
        Args:
            parent: 父窗口
            hosts_manager: HostsManager 实例
            on_close: 窗口关闭时的回调函数
        """
        pass
    
    def show(self):
        """显示窗口"""
        pass
    
    def refresh(self):
        """刷新条目列表"""
        pass
    
    def _load_entries(self) -> List[Tuple[str, str]]:
        """加载所有 hosts 条目"""
        pass
    
    def _filter_entries(self, query: str) -> List[Tuple[str, str]]:
        """根据搜索词过滤条目"""
        pass
    
    def _delete_entry(self, domain: str):
        """删除指定条目"""
        pass
    
    def _delete_all(self):
        """删除所有条目"""
        pass
```

### 2. EntryCard (条目卡片组件)

```python
class EntryCard(tk.Frame):
    """iOS 风格的条目卡片"""
    
    # iOS 风格配色
    BG_COLOR = "#FFFFFF"
    HOVER_COLOR = "#F5F5F7"
    SELECTED_COLOR = "#E8F4FD"
    BORDER_COLOR = "#E5E5EA"
    TEXT_PRIMARY = "#1D1D1F"
    TEXT_SECONDARY = "#86868B"
    DELETE_COLOR = "#FF3B30"
    
    def __init__(self, parent, domain: str, ip: str, on_delete: Callable):
        """
        初始化条目卡片
        
        Args:
            parent: 父容器
            domain: 域名
            ip: IP 地址
            on_delete: 删除回调函数
        """
        pass
    
    def select(self):
        """选中状态"""
        pass
    
    def deselect(self):
        """取消选中"""
        pass
```

### 3. IOSStyleWidgets (iOS 风格组件工具类)

```python
class IOSStyleWidgets:
    """iOS 风格 UI 组件工具类"""
    
    # 颜色常量
    BACKGROUND = "#F5F5F7"
    CARD_BG = "#FFFFFF"
    ACCENT = "#007AFF"
    DESTRUCTIVE = "#FF3B30"
    TEXT_PRIMARY = "#1D1D1F"
    TEXT_SECONDARY = "#86868B"
    BORDER = "#E5E5EA"
    
    @staticmethod
    def create_rounded_frame(parent, **kwargs) -> tk.Frame:
        """创建圆角边框的 Frame"""
        pass
    
    @staticmethod
    def create_search_entry(parent, placeholder: str, on_change: Callable) -> tk.Entry:
        """创建 iOS 风格搜索框"""
        pass
    
    @staticmethod
    def create_action_button(parent, text: str, command: Callable, 
                            style: str = "default") -> tk.Button:
        """
        创建 iOS 风格按钮
        
        Args:
            style: "default", "primary", "destructive"
        """
        pass
```

## Data Models

复用现有的数据模型，新增用于 Hosts Viewer 的数据结构：

```python
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class HostsEntry:
    """Hosts 文件条目"""
    ip: str
    domain: str
    
    def matches(self, query: str) -> bool:
        """检查是否匹配搜索词"""
        query = query.lower()
        return query in self.domain.lower() or query in self.ip

# 类型别名
HostsEntryList = List[HostsEntry]
```

## iOS Style Design Specifications

### 颜色方案

| 用途 | 颜色值 | 说明 |
|------|--------|------|
| 背景色 | #F5F5F7 | 浅灰色背景 |
| 卡片背景 | #FFFFFF | 纯白卡片 |
| 主色调 | #007AFF | iOS 蓝色 |
| 危险色 | #FF3B30 | iOS 红色 |
| 主文字 | #1D1D1F | 深灰文字 |
| 次要文字 | #86868B | 浅灰文字 |
| 边框色 | #E5E5EA | 浅灰边框 |

### 尺寸规范

| 元素 | 尺寸 |
|------|------|
| 圆角半径 | 10px |
| 卡片内边距 | 16px |
| 卡片间距 | 8px |
| 搜索框高度 | 36px |
| 按钮高度 | 44px |
| 字体大小 (标题) | 16px |
| 字体大小 (副标题) | 14px |

### 字体

- Windows: Segoe UI
- 回退: Arial, sans-serif

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Hosts File Parsing Completeness

*For any* valid hosts file content containing IP-domain mappings, comments, and empty lines, the parser should return exactly all valid IP-domain pairs while excluding comments and empty lines.

**Validates: Requirements 1.1, 1.2**

### Property 2: Entry Deletion Correctness

*For any* domain that exists in the hosts file, after deletion, querying for that domain should return None, and the total entry count should decrease by one.

**Validates: Requirements 3.3**

### Property 3: Search Filter Accuracy

*For any* list of hosts entries and any search query, all returned entries should contain the query string in either the domain or IP field (case-insensitive).

**Validates: Requirements 4.2**

## Administrator Privileges Handling

### 权限检测与处理策略

由于修改 Windows hosts 文件需要管理员权限，采用以下策略：

```python
class AdminHelper:
    """管理员权限辅助类"""
    
    @staticmethod
    def is_admin() -> bool:
        """检查当前是否以管理员身份运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    @staticmethod
    def restart_as_admin():
        """以管理员身份重新启动程序"""
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)
    
    @staticmethod
    def request_admin_if_needed(action_name: str) -> bool:
        """
        如果需要管理员权限，提示用户
        
        Returns:
            True 如果已有权限或用户同意重启
            False 如果用户取消
        """
        if AdminHelper.is_admin():
            return True
        
        result = messagebox.askyesno(
            "需要管理员权限",
            f"执行 {action_name} 需要管理员权限。\n\n"
            "是否以管理员身份重新启动程序？"
        )
        
        if result:
            AdminHelper.restart_as_admin()
        return False
```

### 打包为 EXE 时的权限配置

使用 PyInstaller 打包时，通过 UAC 清单文件自动请求管理员权限：

**方法 1: 使用 --uac-admin 参数**
```bash
pyinstaller --onefile --windowed --uac-admin run.py
```

**方法 2: 使用自定义清单文件 (app.manifest)**
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>
```

然后打包：
```bash
pyinstaller --onefile --windowed --manifest app.manifest run.py
```

### UI 中的权限状态显示

在主窗口状态栏显示当前权限状态：
- ✅ 管理员模式 (绿色)
- ⚠️ 普通模式 - 修改 hosts 需要管理员权限 (黄色)

## Error Handling

### File Access Errors
- 文件不存在: 显示友好提示，建议检查系统
- 权限不足: 提示以管理员身份重新启动，提供一键重启按钮
- 编码问题: 尝试多种编码 (UTF-8, GBK)

### UI Errors
- 空列表: 显示 "暂无 hosts 配置" 提示
- 搜索无结果: 显示 "未找到匹配项" 提示
- 删除失败: 显示具体错误原因，如果是权限问题则提供重启选项

## Testing Strategy

### Unit Tests
- 测试 hosts 文件解析逻辑
- 测试搜索过滤逻辑
- 测试条目删除逻辑

### Property-Based Tests
使用 `hypothesis` 库进行属性测试：

- **Property 1**: 生成随机 hosts 文件内容（包含有效条目、注释、空行），验证解析结果只包含有效条目
- **Property 2**: 生成随机 hosts 条目列表，随机选择一个删除，验证删除后查询返回 None
- **Property 3**: 生成随机条目列表和搜索词，验证过滤结果的正确性

每个属性测试至少运行 100 次迭代。

### Integration Tests
- 测试窗口打开和关闭
- 测试与主窗口的交互
- 测试刷新功能

