"""V2Ray 订阅链接解析器

解析 vless、trojan、vmess 协议链接，提取服务器地址和端口。
"""

import re
import base64
import json
from dataclasses import dataclass
from urllib.parse import urlparse, unquote
from typing import Optional

from cf_proxy_manager.logger import logger


@dataclass
class ParsedNode:
    """解析后的节点信息"""
    protocol: str      # vless, trojan, vmess
    address: str       # IP 或域名
    port: int          # 端口
    name: str          # 节点名称
    is_ip: bool        # 是否为 IP 地址
    raw_link: str      # 原始链接


class V2RayParser:
    """V2Ray 链接解析器"""
    
    # IPv4 地址正则表达式
    IP_PATTERN = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    
    @staticmethod
    def is_ip_address(address: str) -> bool:
        """判断地址是否为 IPv4 格式
        
        Args:
            address: 待检查的地址字符串
            
        Returns:
            True 如果是有效的 IPv4 地址，否则 False
        """
        if not address:
            return False
        return bool(V2RayParser.IP_PATTERN.match(address))
    
    @staticmethod
    def parse(content: str) -> list[ParsedNode]:
        """解析订阅内容，返回节点列表
        
        Args:
            content: 订阅内容文本，可包含多行链接
            
        Returns:
            解析成功的节点列表
        """
        nodes = []
        lines = content.strip().split('\n')
        logger.info(f"开始解析订阅内容，共 {len(lines)} 行")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            node = None
            if line.startswith('vless://'):
                node = V2RayParser.parse_vless(line)
            elif line.startswith('trojan://'):
                node = V2RayParser.parse_trojan(line)
            elif line.startswith('vmess://'):
                node = V2RayParser.parse_vmess(line)
            
            if node:
                nodes.append(node)
            elif line.startswith(('vless://', 'trojan://', 'vmess://')):
                logger.warning(f"无法解析链接: {line[:50]}...")
        
        logger.info(f"解析到 {len(nodes)} 个节点")
        return nodes
    
    @staticmethod
    def parse_vless(link: str) -> Optional[ParsedNode]:
        """解析 vless:// 链接
        
        格式: vless://{uuid}@{address}:{port}?{params}#{name}
        
        Args:
            link: vless 协议链接
            
        Returns:
            ParsedNode 或 None（解析失败时）
        """
        try:
            # 提取节点名称（#后面的部分）
            name = ""
            if '#' in link:
                link_part, name = link.rsplit('#', 1)
                name = unquote(name)
            else:
                link_part = link
            
            # 解析 URL
            parsed = urlparse(link_part)
            if parsed.scheme != 'vless':
                return None
            
            # 提取地址和端口
            address = parsed.hostname
            port = parsed.port
            
            if not address or not port:
                return None
            
            return ParsedNode(
                protocol='vless',
                address=address,
                port=port,
                name=name or f"vless-{address}",
                is_ip=V2RayParser.is_ip_address(address),
                raw_link=link
            )
        except Exception as e:
            logger.warning(f"解析 vless 链接失败: {e}")
            return None
    
    @staticmethod
    def parse_trojan(link: str) -> Optional[ParsedNode]:
        """解析 trojan:// 链接
        
        格式: trojan://{password}@{address}:{port}?{params}#{name}
        
        Args:
            link: trojan 协议链接
            
        Returns:
            ParsedNode 或 None（解析失败时）
        """
        try:
            # 提取节点名称（#后面的部分）
            name = ""
            if '#' in link:
                link_part, name = link.rsplit('#', 1)
                name = unquote(name)
            else:
                link_part = link
            
            # 解析 URL
            parsed = urlparse(link_part)
            if parsed.scheme != 'trojan':
                return None
            
            # 提取地址和端口
            address = parsed.hostname
            port = parsed.port
            
            if not address or not port:
                return None
            
            return ParsedNode(
                protocol='trojan',
                address=address,
                port=port,
                name=name or f"trojan-{address}",
                is_ip=V2RayParser.is_ip_address(address),
                raw_link=link
            )
        except Exception as e:
            logger.warning(f"解析 trojan 链接失败: {e}")
            return None
    
    @staticmethod
    def parse_vmess(link: str) -> Optional[ParsedNode]:
        """解析 vmess:// 链接
        
        格式: vmess://{base64_json}
        JSON 结构: {"add": "address", "port": 443, "ps": "name", ...}
        
        Args:
            link: vmess 协议链接
            
        Returns:
            ParsedNode 或 None（解析失败时）
        """
        try:
            # 移除协议前缀
            if not link.startswith('vmess://'):
                return None
            
            b64_data = link[8:]  # 去掉 'vmess://'
            
            # Base64 解码（处理可能的 padding 问题）
            padding = 4 - len(b64_data) % 4
            if padding != 4:
                b64_data += '=' * padding
            
            decoded = base64.b64decode(b64_data).decode('utf-8')
            config = json.loads(decoded)
            
            # 提取地址和端口
            address = config.get('add', '')
            port = config.get('port', 0)
            name = config.get('ps', '')
            
            if not address:
                return None
            
            # port 可能是字符串或整数
            if isinstance(port, str):
                port = int(port)
            
            if not port:
                return None
            
            return ParsedNode(
                protocol='vmess',
                address=address,
                port=port,
                name=name or f"vmess-{address}",
                is_ip=V2RayParser.is_ip_address(address),
                raw_link=link
            )
        except Exception as e:
            logger.warning(f"解析 vmess 链接失败: {e}")
            return None
