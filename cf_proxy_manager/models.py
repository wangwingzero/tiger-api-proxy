"""
CF Proxy Manager - Data Models
数据模型定义
"""
from dataclasses import dataclass, field
from typing import List, Optional
import json


@dataclass
class IPEntry:
    """IP 条目"""
    ip: str
    port: int = 443
    
    def to_dict(self) -> dict:
        return {"ip": self.ip, "port": self.port}
    
    @classmethod
    def from_dict(cls, data: dict) -> "IPEntry":
        return cls(ip=data["ip"], port=data.get("port", 443))


@dataclass
class TestResult:
    """测速结果"""
    ip_entry: IPEntry
    latency_ms: Optional[float]  # None 表示连接失败
    success: bool
    error_message: str = ""
    packet_loss: float = 0.0  # 丢包率 (0.0 - 100.0)
    test_count: int = 1  # 测试次数
    success_count: int = 0  # 成功次数
    
    @property
    def is_stable(self) -> bool:
        """是否稳定（丢包率 < 20%）"""
        return self.packet_loss < 20.0
    
    @property
    def stability_level(self) -> str:
        """稳定性等级: 'stable', 'unstable', 'failed'"""
        if not self.success:
            return 'failed'
        if self.packet_loss < 10:
            return 'stable'
        if self.packet_loss < 30:
            return 'unstable'
        return 'failed'


@dataclass
class ProxyConfig:
    """代理配置"""
    cf_domain: str
    target_node: str
    full_url: str


@dataclass
class ComparisonService:
    """对比服务"""
    name: str           # 服务名称，如 "宁波节点"
    url: str            # 服务 URL
    description: str = ""  # 描述，如 "阿里云函数计算"
    is_default: bool = False  # 是否为默认服务
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "is_default": self.is_default
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ComparisonService":
        return cls(
            name=data["name"],
            url=data["url"],
            description=data.get("description", ""),
            is_default=data.get("is_default", False)
        )


@dataclass
class ComparisonResult:
    """对比测试结果"""
    service: ComparisonService
    latency_ms: Optional[float]  # None 表示失败
    success: bool
    error_message: str = ""
    improvement_pct: Optional[float] = None  # 相对基准的提升百分比
    is_baseline: bool = False  # 是否为基准测试
    is_optimized: bool = False  # 是否为优选IP测试
    packet_loss: float = 0.0  # 丢包率 (0.0 - 100.0)
    
    @property
    def latency_level(self) -> str:
        """返回延迟等级: 'fast', 'medium', 'slow', 'failed'"""
        if not self.success or self.latency_ms is None:
            return 'failed'
        if self.latency_ms < 200:
            return 'fast'
        if self.latency_ms < 500:
            return 'medium'
        return 'slow'
    
    @property
    def is_stable(self) -> bool:
        """是否稳定（丢包率 < 20%）"""
        return self.packet_loss < 20.0


@dataclass
class Config:
    """完整配置"""
    target_nodes: List[str] = field(default_factory=list)
    current_target_node: str = ""
    cf_proxy_domain: str = ""
    ip_list: List[IPEntry] = field(default_factory=list)
    selected_ip: Optional[str] = None
    theme_mode: str = "system"  # dark, light, system
    comparison_services: List["ComparisonService"] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "target_nodes": self.target_nodes,
            "current_target_node": self.current_target_node,
            "cf_proxy_domain": self.cf_proxy_domain,
            "ip_list": [ip.to_dict() for ip in self.ip_list],
            "selected_ip": self.selected_ip,
            "theme_mode": self.theme_mode,
            "comparison_services": [s.to_dict() for s in self.comparison_services]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        return cls(
            target_nodes=data.get("target_nodes", []),
            current_target_node=data.get("current_target_node", ""),
            cf_proxy_domain=data.get("cf_proxy_domain", ""),
            ip_list=[IPEntry.from_dict(ip) for ip in data.get("ip_list", [])],
            selected_ip=data.get("selected_ip"),
            theme_mode=data.get("theme_mode", "system"),
            comparison_services=[ComparisonService.from_dict(s) for s in data.get("comparison_services", [])]
        )


# 默认配置常量
DEFAULT_TARGET_NODE = "anyrouter.top"

DEFAULT_IPS = [
    IPEntry(ip="103.21.244.78", port=443),
    IPEntry(ip="103.21.244.106", port=443),
    IPEntry(ip="104.25.235.32", port=443),
    IPEntry(ip="188.114.98.205", port=443),
    IPEntry(ip="104.21.52.82", port=443),
]

# 默认对比服务
DEFAULT_COMPARISON_SERVICES = [
    ComparisonService(
        name="a-ocnfniawgw.cn-shanghai.fcapp.run",
        url="https://a-ocnfniawgw.cn-shanghai.fcapp.run",
        description="阿里云函数计算",
        is_default=True
    ),
    ComparisonService(
        name="pmpjfbhq.cn-nb1.rainapp.top",
        url="https://pmpjfbhq.cn-nb1.rainapp.top",
        description="RainApp",
        is_default=True
    ),
    ComparisonService(
        name="anyrouter.top",
        url="https://anyrouter.top",
        description="AnyRouter 反代",
        is_default=True
    ),
    ComparisonService(
        name="betterclau.de",
        url="https://betterclau.de/claude/anyrouter.top",
        description="BetterClaude 反代",
        is_default=True
    ),
]


@dataclass
class HostsEntry:
    """Hosts 文件条目"""
    ip: str
    domain: str
    
    def matches(self, query: str) -> bool:
        """
        检查是否匹配搜索词 (大小写不敏感)
        
        Args:
            query: 搜索词
            
        Returns:
            如果域名或 IP 包含搜索词则返回 True
        """
        if not query:
            return True
        query_lower = query.lower()
        return query_lower in self.domain.lower() or query_lower in self.ip.lower()
    
    def to_dict(self) -> dict:
        return {"ip": self.ip, "domain": self.domain}
    
    @classmethod
    def from_dict(cls, data: dict) -> "HostsEntry":
        return cls(ip=data["ip"], domain=data["domain"])
