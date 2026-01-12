# V2Ray 订阅导入功能设计文档

## 概述

本文档描述 V2Ray 订阅导入功能的技术设计，包括模块架构、数据流和接口定义。

## 架构设计

### 模块结构

```
cf_proxy_manager/
├── v2ray_parser.py      # V2Ray 链接解析器
├── dns_resolver.py      # DNS 域名解析器
└── components/
    └── import_dialog.py # 导入对话框 UI
```

### 数据流

```
用户粘贴订阅内容
       ↓
V2RayParser.parse()
       ↓
┌──────────────────┐
│ 提取的地址列表   │
│ - IP 地址        │
│ - 域名           │
└──────────────────┘
       ↓
DNSResolver.resolve_domains()
       ↓
┌──────────────────┐
│ 最终 IP 列表     │
└──────────────────┘
       ↓
ConfigManager.add_ips()
       ↓
GUI 刷新显示
```

## 模块设计

### 1. V2RayParser (v2ray_parser.py)

负责解析 V2Ray/Xray 订阅链接，提取服务器地址。

#### 数据模型

```python
@dataclass
class ParsedNode:
    """解析后的节点信息"""
    protocol: str          # vless, trojan, vmess
    address: str           # IP 或域名
    port: int              # 端口
    name: str              # 节点名称
    is_ip: bool            # 是否为 IP 地址
    raw_link: str          # 原始链接
```

#### 接口定义

```python
class V2RayParser:
    @staticmethod
    def parse(content: str) -> list[ParsedNode]:
        """解析订阅内容，返回节点列表"""
        pass
    
    @staticmethod
    def parse_vless(link: str) -> ParsedNode | None:
        """解析 vless:// 链接"""
        pass
    
    @staticmethod
    def parse_trojan(link: str) -> ParsedNode | None:
        """解析 trojan:// 链接"""
        pass
    
    @staticmethod
    def parse_vmess(link: str) -> ParsedNode | None:
        """解析 vmess:// 链接 (Base64 JSON)"""
        pass
    
    @staticmethod
    def is_ip_address(address: str) -> bool:
        """判断地址是否为 IP 格式"""
        pass
```

#### 链接格式

**vless://**
```
vless://{uuid}@{address}:{port}?{params}#{name}
```

**trojan://**
```
trojan://{password}@{address}:{port}?{params}#{name}
```

**vmess://**
```
vmess://{base64_json}
# JSON 结构: {"add": "address", "port": 443, "ps": "name", ...}
```

### 2. DNSResolver (dns_resolver.py)

负责将域名解析为 IP 地址。

#### 接口定义

```python
class DNSResolver:
    @staticmethod
    def resolve(domain: str) -> list[str]:
        """解析域名，返回 IP 列表"""
        pass
    
    @staticmethod
    def resolve_batch(domains: list[str], 
                      callback: Callable[[str, list[str]], None] = None
                      ) -> dict[str, list[str]]:
        """批量解析域名，支持进度回调"""
        pass
```

#### 实现方式

使用 Python 标准库 `socket.getaddrinfo()` 进行 DNS 解析：

```python
import socket

def resolve(domain: str) -> list[str]:
    try:
        results = socket.getaddrinfo(domain, None, socket.AF_INET)
        return list(set(r[4][0] for r in results))
    except socket.gaierror:
        return []
```

### 3. ImportDialog (components/import_dialog.py)

导入对话框 UI 组件。

#### 界面布局

```
┌─────────────────────────────────────────────┐
│ 导入 V2Ray 订阅                        [X] │
├─────────────────────────────────────────────┤
│ 粘贴订阅内容:                               │
│ ┌─────────────────────────────────────────┐ │
│ │                                         │ │
│ │ (多行文本输入框)                        │ │
│ │                                         │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ☑ 自动解析域名为 IP                         │
│ ☑ 跳过重复 IP                               │
│                                             │
│ 预览:                                       │
│ ┌─────────────────────────────────────────┐ │
│ │ 检测到 5 个节点:                        │ │
│ │ • IP 地址: 3 个                         │ │
│ │ • 域名: 2 个 (待解析)                   │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│              [取消]  [解析并导入]           │
└─────────────────────────────────────────────┘
```

#### 接口定义

```python
class ImportDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_import: Callable[[list[str]], None]):
        """
        Args:
            parent: 父窗口
            on_import: 导入回调，参数为 IP 列表
        """
        pass
    
    def _on_text_change(self, event):
        """文本变化时更新预览"""
        pass
    
    def _on_import_click(self):
        """点击导入按钮"""
        pass
```

## 集成设计

### GUI 集成 (gui_ctk.py)

在主界面添加"导入订阅"按钮：

```python
# 在 IP 列表区域添加按钮
self.import_btn = ctk.CTkButton(
    self.ip_frame,
    text="导入订阅",
    command=self._show_import_dialog
)

def _show_import_dialog(self):
    """显示导入对话框"""
    dialog = ImportDialog(self, on_import=self._on_import_ips)
    dialog.grab_set()

def _on_import_ips(self, ips: list[str]):
    """处理导入的 IP 列表"""
    added = 0
    for ip in ips:
        if ip not in self.config.ips:
            self.config.ips.append(ip)
            added += 1
    self._save_config()
    self._refresh_ip_list()
    self._update_status(f"导入完成: 新增 {added} 个 IP")
```

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| 无效链接格式 | 跳过并记录日志 |
| Base64 解码失败 | 跳过并记录日志 |
| DNS 解析失败 | 跳过并显示警告 |
| 网络超时 | 显示错误提示 |

## 日志记录

```python
logger.info(f"开始解析订阅内容，共 {len(lines)} 行")
logger.info(f"解析到 {len(nodes)} 个节点")
logger.info(f"DNS 解析: {domain} -> {ips}")
logger.warning(f"无法解析链接: {link[:50]}...")
logger.error(f"DNS 解析失败: {domain}")
```

## 正确性属性

*正确性属性是应该在系统所有有效执行中保持为真的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### Property 1: vless/trojan 解析往返一致性
*For any* 有效的 vless 或 trojan 链接，解析后提取的地址和端口应该与原始链接中的值完全匹配。
**Validates: Requirements 1.1, 1.2**

### Property 2: vmess Base64 解码一致性
*For any* 有效的 vmess 链接（Base64 编码的 JSON），解码并解析后提取的地址和端口应该与 JSON 中的 "add" 和 "port" 字段值匹配。
**Validates: Requirements 1.3**

### Property 3: IP 地址识别准确性
*For any* 字符串，`is_ip_address()` 返回 `True` 当且仅当该字符串是有效的 IPv4 地址格式（四个 0-255 的数字用点分隔）。
**Validates: Requirements 1.4, 1.5**

### Property 4: 导入去重正确性
*For any* IP 列表和现有配置，导入后配置中的 IP 数量应该等于原有数量加上新增的不重复 IP 数量。
**Validates: Requirements 3.1, 3.2**

### Property 5: 导入统计准确性
*For any* 导入操作，报告的"新增"数量加上"跳过"数量应该等于输入 IP 列表的总数。
**Validates: Requirements 3.3**

### Property 6: 预览统计准确性
*For any* 解析结果，预览显示的 IP 数量加上域名数量应该等于解析到的节点总数。
**Validates: Requirements 4.4**

## 测试策略

### 双重测试方法

- **单元测试**: 验证特定示例、边界情况和错误条件
- **属性测试**: 使用 hypothesis 库验证跨所有输入的通用属性

### 属性测试配置

- 使用 `hypothesis` 库进行属性测试
- 每个属性测试最少运行 100 次迭代
- 每个测试必须引用设计文档中的属性
- 标签格式: **Feature: v2ray-import, Property {number}: {property_text}**

## 依赖

- 无需新增外部依赖
- 使用 Python 标准库: `socket`, `base64`, `json`, `urllib.parse`, `re`
- 测试依赖: `hypothesis`, `pytest`
