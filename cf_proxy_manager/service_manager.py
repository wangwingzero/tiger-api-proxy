"""
CF Proxy Manager - Service Manager
对比服务管理模块
"""
from typing import List, Optional
from .models import ComparisonService, DEFAULT_COMPARISON_SERVICES
from .parsers import URLParser


class ServiceManager:
    """对比服务管理器"""
    
    def __init__(self, services: Optional[List[ComparisonService]] = None):
        """
        初始化服务管理器
        
        Args:
            services: 初始服务列表，如果为空则使用默认列表
        """
        if services is None or len(services) == 0:
            self.services = list(DEFAULT_COMPARISON_SERVICES)
        else:
            self.services = list(services)
    
    def add_service(self, name: str, url: str, description: str = "") -> bool:
        """
        添加对比服务
        
        Args:
            name: 服务名称
            url: 服务 URL（必须是有效的 HTTPS URL）
            description: 服务描述
            
        Returns:
            True 如果添加成功，False 如果 URL 无效或服务已存在
        """
        # 验证 URL
        if not URLParser.is_valid_https_url(url):
            return False
        
        # 检查是否已存在
        if self.find_by_url(url) is not None:
            return False
        
        service = ComparisonService(
            name=name,
            url=url,
            description=description,
            is_default=False
        )
        self.services.append(service)
        return True
    
    def remove_service(self, url: str) -> bool:
        """
        移除对比服务
        
        Args:
            url: 要移除的服务 URL
            
        Returns:
            True 如果移除成功，False 如果服务不存在
        """
        original_len = len(self.services)
        self.services = [s for s in self.services if s.url != url]
        return len(self.services) < original_len
    
    def reset_to_defaults(self) -> None:
        """重置为默认服务列表"""
        self.services = list(DEFAULT_COMPARISON_SERVICES)
    
    def find_by_url(self, url: str) -> Optional[ComparisonService]:
        """根据 URL 查找服务"""
        for service in self.services:
            if service.url == url:
                return service
        return None
    
    def find_by_name(self, name: str) -> Optional[ComparisonService]:
        """根据名称查找服务"""
        for service in self.services:
            if service.name == name:
                return service
        return None
    
    def get_all(self) -> List[ComparisonService]:
        """获取所有服务"""
        return list(self.services)
    
    def get_default_services(self) -> List[ComparisonService]:
        """获取默认服务列表"""
        return list(DEFAULT_COMPARISON_SERVICES)
    
    def is_default_list(self) -> bool:
        """检查当前列表是否为默认列表"""
        if len(self.services) != len(DEFAULT_COMPARISON_SERVICES):
            return False
        
        for s1, s2 in zip(self.services, DEFAULT_COMPARISON_SERVICES):
            if s1.url != s2.url:
                return False
        
        return True
