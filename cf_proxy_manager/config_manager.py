"""
CF Proxy Manager - Configuration Manager
配置管理模块
"""
import json
import os
from typing import Optional
from .models import Config, IPEntry, DEFAULT_TARGET_NODE, DEFAULT_IPS


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
    
    def load(self) -> Config:
        """加载配置文件，如不存在则返回默认配置"""
        if not os.path.exists(self.config_path):
            return self.get_default_config()
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Config.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            return self.get_default_config()
    
    def save(self, config: Config) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except (IOError, OSError):
            return False
    
    def get_default_config(self) -> Config:
        """返回默认配置"""
        return Config(
            target_nodes=[DEFAULT_TARGET_NODE],
            current_target_node=DEFAULT_TARGET_NODE,
            cf_proxy_domain="",
            ip_list=list(DEFAULT_IPS),
            selected_ip=None
        )
