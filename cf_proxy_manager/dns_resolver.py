"""DNS 域名解析器

将域名解析为 IP 地址，支持单个和批量解析。
"""

import socket
from typing import Callable, Optional

from cf_proxy_manager.logger import logger


class DNSResolver:
    """DNS 域名解析器"""
    
    @staticmethod
    def resolve(domain: str, timeout: float = 5.0) -> list[str]:
        """解析单个域名，返回 IP 列表
        
        Args:
            domain: 要解析的域名
            timeout: 超时时间（秒）
            
        Returns:
            解析到的 IP 地址列表，失败时返回空列表
        """
        try:
            # 设置超时
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout)
            
            try:
                # 获取 IPv4 地址
                results = socket.getaddrinfo(domain, None, socket.AF_INET)
                # 去重
                ips = list(set(r[4][0] for r in results))
                logger.info(f"DNS 解析: {domain} -> {ips}")
                return ips
            finally:
                # 恢复原超时设置
                socket.setdefaulttimeout(old_timeout)
                
        except socket.gaierror as e:
            logger.error(f"DNS 解析失败: {domain} - {e}")
            return []
        except socket.timeout:
            logger.error(f"DNS 解析超时: {domain}")
            return []
        except Exception as e:
            logger.error(f"DNS 解析异常: {domain} - {e}")
            return []
    
    @staticmethod
    def resolve_batch(
        domains: list[str],
        callback: Optional[Callable[[str, list[str]], None]] = None,
        timeout: float = 5.0
    ) -> dict[str, list[str]]:
        """批量解析域名
        
        Args:
            domains: 要解析的域名列表
            callback: 进度回调函数，参数为 (domain, ips)
            timeout: 每个域名的超时时间（秒）
            
        Returns:
            域名到 IP 列表的映射字典
        """
        results = {}
        total = len(domains)
        
        logger.info(f"开始批量 DNS 解析，共 {total} 个域名")
        
        for i, domain in enumerate(domains, 1):
            ips = DNSResolver.resolve(domain, timeout)
            results[domain] = ips
            
            if callback:
                callback(domain, ips)
            
            logger.debug(f"DNS 解析进度: {i}/{total}")
        
        # 统计结果
        success = sum(1 for ips in results.values() if ips)
        failed = total - success
        logger.info(f"批量 DNS 解析完成: 成功 {success}, 失败 {failed}")
        
        return results
