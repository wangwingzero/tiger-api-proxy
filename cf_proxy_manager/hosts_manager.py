"""
CF Proxy Manager - Hosts File Manager
Hosts 文件管理模块
"""
import os
import re
import shutil
import subprocess
from datetime import datetime
from typing import Optional, Tuple, List

from .models import HostsEntry


class HostsManager:
    """Hosts 文件管理器"""
    
    HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
    BACKUP_DIR = os.path.join(os.path.expanduser("~"), ".cf_proxy_manager", "backups")
    
    # 匹配 hosts 条目的正则: IP 域名
    ENTRY_PATTERN = re.compile(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\S+)')
    
    def __init__(self, hosts_path: Optional[str] = None):
        self.hosts_path = hosts_path or self.HOSTS_PATH
    
    def read_hosts(self) -> str:
        """读取 hosts 文件内容"""
        try:
            with open(self.hosts_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(self.hosts_path, 'r', encoding='gbk') as f:
                return f.read()
    
    def get_entry(self, domain: str) -> Optional[Tuple[str, str]]:
        """
        获取指定域名的 hosts 条目
        
        Returns:
            (ip, domain) 元组，如果不存在则返回 None
        """
        content = self.read_hosts()
        
        for line in content.splitlines():
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            
            match = self.ENTRY_PATTERN.match(line)
            if match:
                ip, host = match.groups()
                if host.lower() == domain.lower():
                    return (ip, host)
        
        return None
    
    def update_entry(self, domain: str, ip: str) -> bool:
        """
        更新或添加 hosts 条目
        
        Returns:
            是否成功
        """
        try:
            content = self.read_hosts()
            lines = content.splitlines()
            
            # 查找是否已存在该域名的条目
            found = False
            new_lines = []
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#') or not stripped:
                    new_lines.append(line)
                    continue
                
                match = self.ENTRY_PATTERN.match(stripped)
                if match:
                    _, host = match.groups()
                    if host.lower() == domain.lower():
                        # 替换为新条目
                        new_lines.append(f"{ip} {domain}")
                        found = True
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            # 如果没找到，添加新条目
            if not found:
                new_lines.append(f"{ip} {domain}")
            
            # 写入文件
            new_content = '\n'.join(new_lines)
            if not new_content.endswith('\n'):
                new_content += '\n'
            
            with open(self.hosts_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        except PermissionError:
            return False
        except Exception:
            return False
    
    def remove_entry(self, domain: str) -> bool:
        """
        删除指定域名的 hosts 条目
        
        Returns:
            是否成功
        """
        try:
            content = self.read_hosts()
            lines = content.splitlines()
            
            new_lines = []
            removed = False
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#') or not stripped:
                    new_lines.append(line)
                    continue
                
                match = self.ENTRY_PATTERN.match(stripped)
                if match:
                    _, host = match.groups()
                    if host.lower() == domain.lower():
                        # 跳过这一行（删除）
                        removed = True
                        continue
                
                new_lines.append(line)
            
            if not removed:
                return True  # 本来就不存在，视为成功
            
            # 写入文件
            new_content = '\n'.join(new_lines)
            if not new_content.endswith('\n'):
                new_content += '\n'
            
            with open(self.hosts_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        except PermissionError:
            return False
        except Exception:
            return False
    
    def backup(self) -> Optional[str]:
        """
        备份 hosts 文件
        
        Returns:
            备份文件路径，失败返回 None
        """
        try:
            # 确保备份目录存在
            os.makedirs(self.BACKUP_DIR, exist_ok=True)
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.BACKUP_DIR, f"hosts_{timestamp}.bak")
            
            # 复制文件
            shutil.copy2(self.hosts_path, backup_path)
            
            return backup_path
        except Exception:
            return None
    
    @staticmethod
    def flush_dns() -> bool:
        """
        刷新 DNS 缓存
        
        Returns:
            是否成功
        """
        try:
            result = subprocess.run(
                ['ipconfig', '/flushdns'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def format_entry(ip: str, domain: str) -> str:
        """格式化 hosts 条目"""
        return f"{ip} {domain}"
    
    @staticmethod
    def parse_entry(line: str) -> Optional[Tuple[str, str]]:
        """
        解析 hosts 条目
        
        Returns:
            (ip, domain) 元组，解析失败返回 None
        """
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        
        match = HostsManager.ENTRY_PATTERN.match(line)
        if match:
            return match.groups()
        
        return None
    
    def get_all_entries(self) -> List[HostsEntry]:
        """
        获取所有 hosts 条目
        
        Returns:
            HostsEntry 列表，过滤掉注释和空行
        """
        entries = []
        try:
            content = self.read_hosts()
            
            for line in content.splitlines():
                parsed = self.parse_entry(line)
                if parsed:
                    ip, domain = parsed
                    entries.append(HostsEntry(ip=ip, domain=domain))
        except Exception:
            pass
        
        return entries
    
    def filter_entries(self, query: str) -> List[HostsEntry]:
        """
        根据搜索词过滤 hosts 条目
        
        Args:
            query: 搜索词
            
        Returns:
            匹配的 HostsEntry 列表
        """
        all_entries = self.get_all_entries()
        if not query:
            return all_entries
        return [entry for entry in all_entries if entry.matches(query)]
