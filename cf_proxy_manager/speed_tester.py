"""
CF Proxy Manager - Speed Tester
测速模块
"""
import socket
import time
from typing import List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from .models import IPEntry, TestResult


class SpeedTester:
    """IP 测速器"""
    
    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout
    
    def _test_single_port(self, ip: str, port: int) -> TestResult:
        """测试单个 IP 单个端口的 TCP 连接延迟"""
        ip_entry = IPEntry(ip=ip, port=port)
        
        try:
            start_time = time.perf_counter()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            sock.connect((ip, port))
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            sock.close()
            
            return TestResult(
                ip_entry=ip_entry,
                latency_ms=round(latency_ms, 2),
                success=True
            )
        except socket.timeout:
            return TestResult(
                ip_entry=ip_entry,
                latency_ms=None,
                success=False,
                error_message="Connection timeout"
            )
        except socket.error as e:
            return TestResult(
                ip_entry=ip_entry,
                latency_ms=None,
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            return TestResult(
                ip_entry=ip_entry,
                latency_ms=None,
                success=False,
                error_message=str(e)
            )
    
    def test_ip(self, ip: str, port: int = 443) -> TestResult:
        """
        测试单个 IP 的 TCP 连接延迟
        
        端口回退机制：先尝试 443，如果失败则尝试 80
        """
        # 先尝试指定端口（默认 443）
        result = self._test_single_port(ip, port)
        if result.success:
            return result
        
        # 如果 443 失败，尝试 80
        if port == 443:
            fallback_result = self._test_single_port(ip, 80)
            if fallback_result.success:
                return fallback_result
        
        # 都失败了，返回原始结果
        return result
    
    def test_all(
        self, 
        ip_list: List[IPEntry], 
        callback: Optional[Callable[[int, int, TestResult], None]] = None,
        max_workers: int = 5
    ) -> List[TestResult]:
        """
        测试所有 IP，支持进度回调
        
        Args:
            ip_list: IP 列表
            callback: 进度回调函数 (current, total, result)
            max_workers: 最大并发数
        
        Returns:
            测试结果列表
        """
        results = []
        total = len(ip_list)
        
        if total == 0:
            return results
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_ip = {
                executor.submit(self.test_ip, ip.ip, ip.port): ip 
                for ip in ip_list
            }
            
            # 收集结果
            completed = 0
            for future in as_completed(future_to_ip):
                result = future.result()
                results.append(result)
                completed += 1
                
                if callback:
                    callback(completed, total, result)
        
        return results
    
    @staticmethod
    def get_best_ip(results: List[TestResult]) -> Optional[TestResult]:
        """从测试结果中获取最佳 IP (延迟最低的成功结果)"""
        successful = [r for r in results if r.success and r.latency_ms is not None]
        
        if not successful:
            return None
        
        return min(successful, key=lambda r: r.latency_ms)
    
    @staticmethod
    def sort_results(results: List[TestResult]) -> List[TestResult]:
        """
        排序测试结果
        成功的按延迟升序排列，失败的放在最后
        """
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        # 成功的按延迟排序
        successful.sort(key=lambda r: r.latency_ms if r.latency_ms is not None else float('inf'))
        
        return successful + failed
