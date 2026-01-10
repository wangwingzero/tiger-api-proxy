"""
CF Proxy Manager - URL and IP Parsers
URL 和 IP 解析模块
"""
import re
from typing import List, Optional
from urllib.parse import urlparse
from .models import IPEntry, ProxyConfig


class URLParser:
    """URL 解析器"""
    
    @staticmethod
    def parse_proxy_url(url: str) -> Optional[ProxyConfig]:
        """
        解析完整代理 URL 或域名
        支持格式:
        - https://betterclau.de/claude/anyrouter.top
        - betterclau.de
        """
        url = url.strip()
        if not url:
            return None
        
        # 如果没有协议，添加 https://
        if not url.startswith(('http://', 'https://')):
            # 检查是否是纯域名
            if '/' not in url:
                return ProxyConfig(
                    cf_domain=url,
                    target_node="",
                    full_url=""
                )
            url = 'https://' + url
        
        try:
            parsed = urlparse(url)
            cf_domain = parsed.netloc
            
            # 提取目标节点 (路径的最后一部分)
            path_parts = [p for p in parsed.path.split('/') if p]
            target_node = path_parts[-1] if path_parts else ""
            
            return ProxyConfig(
                cf_domain=cf_domain,
                target_node=target_node,
                full_url=url
            )
        except Exception:
            return None
    
    @staticmethod
    def build_proxy_url(cf_domain: str, target_node: str) -> str:
        """构建完整的代理 URL"""
        cf_domain = cf_domain.strip()
        target_node = target_node.strip()
        
        # 移除协议前缀
        if cf_domain.startswith(('http://', 'https://')):
            cf_domain = URLParser.extract_domain(cf_domain)
        
        if not cf_domain:
            return ""
        
        if not target_node:
            return f"https://{cf_domain}"
        
        return f"https://{cf_domain}/claude/{target_node}"
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """从 URL 中提取域名"""
        url = url.strip()
        if not url:
            return ""
        
        if not url.startswith(('http://', 'https://')):
            # 可能是纯域名
            if '/' in url:
                return url.split('/')[0]
            return url
        
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """验证 URL 格式"""
        url = url.strip()
        if not url:
            return False
        
        # 纯域名也是有效的
        if not url.startswith(('http://', 'https://')):
            # 简单的域名验证
            domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}(/.*)?$'
            return bool(re.match(domain_pattern, url))
        
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc)
        except Exception:
            return False


class IPParser:
    """IP 解析器"""
    
    IP_PATTERN = re.compile(
        r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::(\d+))?(?:#.*)?$'
    )
    
    @staticmethod
    def parse(entry: str) -> Optional[IPEntry]:
        """
        解析 IP 条目
        支持格式:
        - 103.21.244.78
        - 103.21.244.78:443
        - 103.21.244.78:443#🇩🇪 法兰克福
        """
        entry = entry.strip()
        if not entry:
            return None
        
        match = IPParser.IP_PATTERN.match(entry)
        if not match:
            return None
        
        ip = match.group(1)
        port_str = match.group(2)
        port = int(port_str) if port_str else 443
        
        # 验证 IP 格式
        if not IPParser.is_valid_ip(ip):
            return None
        
        # 验证端口范围
        if not (1 <= port <= 65535):
            return None
        
        return IPEntry(ip=ip, port=port)
    
    @staticmethod
    def parse_multiple(text: str) -> List[IPEntry]:
        """解析多行或逗号分隔的 IP 列表"""
        entries = []
        
        # 支持换行和逗号分隔
        lines = text.replace(',', '\n').split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            ip_entry = IPParser.parse(line)
            if ip_entry:
                entries.append(ip_entry)
        
        return entries
    
    @staticmethod
    def format(ip_entry: IPEntry) -> str:
        """格式化 IP 条目为字符串"""
        return f"{ip_entry.ip}:{ip_entry.port}"
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """验证 IP 地址格式"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            try:
                num = int(part)
                if not (0 <= num <= 255):
                    return False
            except ValueError:
                return False
        
        return True
