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


@dataclass
class ProxyConfig:
    """代理配置"""
    cf_domain: str
    target_node: str
    full_url: str


@dataclass
class Config:
    """完整配置"""
    target_nodes: List[str] = field(default_factory=list)
    current_target_node: str = ""
    cf_proxy_domain: str = ""
    ip_list: List[IPEntry] = field(default_factory=list)
    selected_ip: Optional[str] = None
    theme_mode: str = "system"  # dark, light, system
    
    def to_dict(self) -> dict:
        return {
            "target_nodes": self.target_nodes,
            "current_target_node": self.current_target_node,
            "cf_proxy_domain": self.cf_proxy_domain,
            "ip_list": [ip.to_dict() for ip in self.ip_list],
            "selected_ip": self.selected_ip,
            "theme_mode": self.theme_mode
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        return cls(
            target_nodes=data.get("target_nodes", []),
            current_target_node=data.get("current_target_node", ""),
            cf_proxy_domain=data.get("cf_proxy_domain", ""),
            ip_list=[IPEntry.from_dict(ip) for ip in data.get("ip_list", [])],
            selected_ip=data.get("selected_ip"),
            theme_mode=data.get("theme_mode", "system")
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
