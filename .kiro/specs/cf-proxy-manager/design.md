# Design Document: CF Proxy Manager

## Overview

CF Proxy Manager 是一个基于 Python + Tkinter 的 Windows GUI 应用程序，用于管理 Cloudflare 反向代理配置和优选 IP。应用采用模块化设计，将 UI、测速、配置管理和系统操作分离，确保代码可维护性和可测试性。

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CF Proxy Manager                      │
├─────────────────────────────────────────────────────────┤
│                      GUI Layer                           │
│  ┌─────────────┬─────────────┬─────────────────────┐   │
│  │ Target Node │  CF Proxy   │    IP Management    │   │
│  │   Section   │   Section   │      Section        │   │
│  └─────────────┴─────────────┴─────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│                    Core Services                         │
│  ┌─────────────┬─────────────┬─────────────────────┐   │
│  │   Config    │   Speed     │      Hosts          │   │
│  │   Manager   │   Tester    │      Manager        │   │
│  └─────────────┴─────────────┴─────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│                    System Layer                          │
│  ┌─────────────┬─────────────┬─────────────────────┐   │
│  │    File     │   Network   │      Admin          │   │
│  │    I/O      │   Socket    │      Privileges     │   │
│  └─────────────┴─────────────┴─────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. ConfigManager

负责配置的加载、保存和管理。

```python
class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        """初始化配置管理器"""
        pass
    
    def load(self) -> Config:
        """加载配置文件，如不存在则返回默认配置"""
        pass
    
    def save(self, config: Config) -> bool:
        """保存配置到文件"""
        pass
    
    def get_default_config(self) -> Config:
        """返回默认配置"""
        pass
```

### 2. SpeedTester

负责测试 IP 延迟。

```python
class SpeedTester:
    def __init__(self, timeout: float = 3.0):
        """初始化测速器"""
        pass
    
    def test_ip(self, ip: str, port: int = 443) -> TestResult:
        """测试单个 IP 的 TCP 连接延迟"""
        pass
    
    def test_all(self, ip_list: List[IPEntry], callback: Callable = None) -> List[TestResult]:
        """测试所有 IP，支持进度回调"""
        pass
    
    def get_best_ip(self, results: List[TestResult]) -> Optional[TestResult]:
        """从测试结果中获取最佳 IP"""
        pass
```

### 3. HostsManager

负责 hosts 文件的读写操作。

```python
class HostsManager:
    HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
    
    def __init__(self):
        """初始化 hosts 管理器"""
        pass
    
    def read_hosts(self) -> str:
        """读取 hosts 文件内容"""
        pass
    
    def get_entry(self, domain: str) -> Optional[str]:
        """获取指定域名的 hosts 条目"""
        pass
    
    def update_entry(self, domain: str, ip: str) -> bool:
        """更新或添加 hosts 条目"""
        pass
    
    def remove_entry(self, domain: str) -> bool:
        """删除指定域名的 hosts 条目，恢复默认 DNS 解析"""
        pass
    
    def backup(self) -> str:
        """备份 hosts 文件，返回备份路径"""
        pass
    
    def flush_dns(self) -> bool:
        """刷新 DNS 缓存"""
        pass
```

### 4. URLParser

负责解析和构建代理 URL。

```python
class URLParser:
    @staticmethod
    def parse_proxy_url(url: str) -> ProxyConfig:
        """解析完整代理 URL 或域名"""
        pass
    
    @staticmethod
    def build_proxy_url(cf_domain: str, target_node: str) -> str:
        """构建完整的代理 URL"""
        pass
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """从 URL 中提取域名"""
        pass
```

### 5. IPParser

负责解析 IP 条目。

```python
class IPParser:
    @staticmethod
    def parse(entry: str) -> IPEntry:
        """解析 IP 条目，支持格式: IP:PORT#LOCATION 或 IP"""
        pass
    
    @staticmethod
    def parse_multiple(text: str) -> List[IPEntry]:
        """解析多行或逗号分隔的 IP 列表"""
        pass
    
    @staticmethod
    def format(ip_entry: IPEntry) -> str:
        """格式化 IP 条目为字符串"""
        pass
```

## Data Models

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

@dataclass
class IPEntry:
    ip: str
    port: int = 443

@dataclass
class TestResult:
    ip_entry: IPEntry
    latency_ms: Optional[float]  # None 表示连接失败
    success: bool
    error_message: str = ""

@dataclass
class ProxyConfig:
    cf_domain: str
    target_node: str
    full_url: str

@dataclass
class Config:
    target_nodes: List[str]
    current_target_node: str
    cf_proxy_domain: str
    ip_list: List[IPEntry]
    selected_ip: Optional[str]

# 默认配置
DEFAULT_TARGET_NODE = "anyrouter.top"

DEFAULT_IPS = [
    IPEntry(ip="103.21.244.78", port=443),
    IPEntry(ip="103.21.244.106", port=443),
    IPEntry(ip="104.25.235.32", port=443),
    IPEntry(ip="188.114.98.205", port=443),
    IPEntry(ip="104.21.52.82", port=443),
]
```

## GUI Layout

```
┌──────────────────────────────────────────────────────────────┐
│  CF Proxy Manager                                      [─][□][×]│
├──────────────────────────────────────────────────────────────┤
│ ┌─ 目标反代节点 ──────────────────────────────────────────┐ │
│ │ 当前节点: [anyrouter.top                    ▼] [添加]   │ │
│ │ 已保存节点: anyrouter.top | a-ocnfniawgw.cn-shanghai... │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─ CF 反代配置 ───────────────────────────────────────────┐ │
│ │ 反代域名/URL: [betterclau.de                          ] │ │
│ │ 完整代理地址: https://betterclau.de/claude/anyrouter.top│ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─ 优选 IP 管理 ──────────────────────────────────────────┐ │
│ │ ┌────────────────────────────────────────────────────┐ │ │
│ │ │ IP                    │ 延迟      │ 状态          │ │ │
│ │ ├────────────────────────────────────────────────────┤ │ │
│ │ │ 103.21.244.78         │ 156ms     │ ✓             │ │ │
│ │ │ 103.21.244.106        │ 162ms     │ ✓             │ │ │
│ │ │ 104.25.235.32         │ 198ms     │ ✓             │ │ │
│ │ │ 188.114.98.205        │ --        │ ✗             │ │ │
│ │ │ 104.21.52.82          │ 89ms      │ ✓ 最佳        │ │ │
│ │ └────────────────────────────────────────────────────┘ │ │
│ │ 添加 IP: [                                    ] [添加]  │ │
│ │                                                        │ │
│ │ [开始测速]  [应用最佳 IP]  [删除选中]  [清除hosts]        │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─ 状态 ─────────────────────────────────────────────────┐ │
│ │ 当前 hosts 配置: betterclau.de -> 104.21.52.82         │ │
│ │ 状态: 已应用最佳 IP                                     │ │
│ └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: URL/Domain Parsing Round Trip

*For any* valid proxy URL (full URL like `https://domain.com/path/target` or domain-only like `domain.com`), parsing and then reconstructing the URL should produce a valid, equivalent proxy configuration.

**Validates: Requirements 1.3, 2.2, 2.3**

### Property 2: IP Entry Parsing Consistency

*For any* IP entry string in supported formats (`IP`, `IP:PORT`, `IP:PORT#LOCATION`), parsing should correctly extract the IP address, port (default 443), and location tag, and formatting the parsed entry should produce an equivalent string.

**Validates: Requirements 3.3, 3.4**

### Property 3: Best IP Selection Correctness

*For any* list of test results with at least one successful result, `get_best_ip()` should return the result with the minimum latency among all successful results.

**Validates: Requirements 4.5**

### Property 4: Failed IP Exclusion

*For any* test result where the connection failed (latency is None), the result should have `success=False` and should not be selected as the best IP.

**Validates: Requirements 4.6**

### Property 5: Test Results Sorting

*For any* list of test results after sorting, successful results should appear before failed results, and successful results should be ordered by ascending latency.

**Validates: Requirements 4.7**

### Property 6: Hosts Entry Format Correctness

*For any* valid domain and IP address, the generated hosts file entry should follow the format `IP DOMAIN` with proper spacing and be parseable back to the original values.

**Validates: Requirements 5.2**

### Property 7: Configuration Round Trip

*For any* valid Config object, serializing to JSON and deserializing should produce an equivalent Config object with all fields preserved (target nodes, CF proxy domain, IP list, selected IP).

**Validates: Requirements 6.1, 6.3**

### Property 8: Target Node List Invariant

*For any* sequence of add operations on the target node list, the list length should equal the number of unique nodes added, and all added nodes should be retrievable.

**Validates: Requirements 1.4, 1.5**

## Error Handling

### Network Errors
- TCP connection timeout: Mark IP as failed, continue testing others
- Socket errors: Log error, mark IP as failed with error message
- All IPs failed: Display warning, suggest checking network

### File System Errors
- Hosts file not found: Display error, suggest running as admin
- Permission denied: Prompt for admin privileges
- Backup failed: Warn user, ask for confirmation before proceeding

### Input Validation Errors
- Invalid URL format: Show inline error, prevent saving
- Invalid IP format: Show inline error, prevent adding
- Empty required fields: Disable action buttons

## Testing Strategy

### Unit Tests
- Test URL parsing with various formats
- Test IP entry parsing with edge cases
- Test hosts entry generation
- Test configuration serialization

### Property-Based Tests
使用 `hypothesis` 库进行属性测试：

- **Property 1**: 生成随机有效 URL，验证解析-重建一致性
- **Property 2**: 生成随机 IP 条目，验证解析-格式化一致性
- **Property 3-5**: 生成随机测试结果列表，验证排序和选择逻辑
- **Property 6**: 生成随机域名和 IP，验证 hosts 条目格式
- **Property 7**: 生成随机配置对象，验证 JSON 序列化往返
- **Property 8**: 生成随机节点添加序列，验证列表不变量

每个属性测试至少运行 100 次迭代。

### Integration Tests
- 测试完整的测速流程（使用 mock socket）
- 测试 hosts 文件修改流程（使用临时文件）
- 测试配置加载和保存流程
