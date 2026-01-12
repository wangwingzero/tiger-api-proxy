"""
CF Proxy Manager - Speed Tester
测速模块（含丢包率测试）
"""
import socket
import time
from typing import List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from .models import IPEntry, TestResult
from .logger import logger


class SpeedTester:
    """IP 测速器（含丢包率测试）"""
    
    def __init__(self, timeout: float = 3.0, test_count: int = 3):
        """
        初始化测速器
        
        Args:
            timeout: 单次连接超时时间（秒）
            test_count: 每个IP测试次数（用于计算丢包率）
        """
        self.timeout = timeout
        self.test_count = test_count
        logger.info(f"SpeedTester 初始化: timeout={timeout}s, test_count={test_count}")
    
    def _test_single_connection(self, ip: str, port: int) -> Optional[float]:
        """
        测试单次 TCP 连接
        
        Returns:
            成功返回延迟(ms)，失败返回 None
        """
        sock = None
        try:
            logger.debug(f"  TCP连接 {ip}:{port}...")
            start_time = time.perf_counter()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            sock.connect((ip, port))
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            logger.debug(f"  连接成功: {latency_ms:.2f}ms")
            return round(latency_ms, 2)
        except socket.timeout as e:
            logger.debug(f"  连接超时: {ip}:{port}")
            return None
        except socket.error as e:
            logger.debug(f"  Socket错误: {ip}:{port} - {e}")
            return None
        except OSError as e:
            logger.debug(f"  OS错误: {ip}:{port} - {e}")
            return None
        except Exception as e:
            logger.debug(f"  未知错误: {ip}:{port} - {type(e).__name__}: {e}")
            return None
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
    
    def test_ip(self, ip: str, port: int = 443) -> TestResult:
        """
        测试单个 IP 的 TCP 连接延迟和丢包率
        
        多次测试计算平均延迟和丢包率
        端口回退机制：先尝试指定端口，如果全部失败则尝试 80
        """
        logger.debug(f"开始测试 IP: {ip}:{port}")
        ip_entry = IPEntry(ip=ip, port=port)
        
        # 多次测试
        latencies = []
        for i in range(self.test_count):
            logger.debug(f"  第{i+1}/{self.test_count}次测试...")
            latency = self._test_single_connection(ip, port)
            if latency is not None:
                latencies.append(latency)
        
        success_count = len(latencies)
        logger.debug(f"  端口{port}测试完成: {success_count}/{self.test_count}成功")
        
        # 如果指定端口全部失败，尝试端口 80
        if success_count == 0 and port == 443:
            logger.debug(f"  端口443全部失败，尝试端口80...")
            for i in range(self.test_count):
                logger.debug(f"  第{i+1}/{self.test_count}次测试(端口80)...")
                latency = self._test_single_connection(ip, 80)
                if latency is not None:
                    latencies.append(latency)
            success_count = len(latencies)
            if success_count > 0:
                ip_entry = IPEntry(ip=ip, port=80)
                logger.debug(f"  端口80测试完成: {success_count}/{self.test_count}成功")
        
        # 计算结果
        if success_count > 0:
            avg_latency = round(sum(latencies) / len(latencies), 2)
            packet_loss = round((1 - success_count / self.test_count) * 100, 1)
            
            logger.info(f"测试完成 {ip}:{ip_entry.port}: 延迟={avg_latency}ms, 丢包={packet_loss}%")
            return TestResult(
                ip_entry=ip_entry,
                latency_ms=avg_latency,
                success=True,
                packet_loss=packet_loss,
                test_count=self.test_count,
                success_count=success_count
            )
        else:
            logger.warning(f"测试失败 {ip}: 所有连接均失败")
            return TestResult(
                ip_entry=ip_entry,
                latency_ms=None,
                success=False,
                error_message="连接失败",
                packet_loss=100.0,
                test_count=self.test_count,
                success_count=0
            )
    
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
        
        logger.info(f"开始批量测速: {total}个IP, 并发数={max_workers}")
        
        if total == 0:
            logger.warning("IP列表为空，跳过测速")
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
                
                logger.debug(f"进度: {completed}/{total} - {result.ip_entry.ip}: {'成功' if result.success else '失败'}")
                
                if callback:
                    callback(completed, total, result)
        
        logger.info(f"批量测速完成: {sum(1 for r in results if r.success)}/{total}成功")
        return results
    
    @staticmethod
    def get_best_ip(results: List[TestResult]) -> Optional[TestResult]:
        """
        从测试结果中获取最佳 IP
        
        选择标准：
        1. 必须成功且稳定（丢包率 < 20%）
        2. 延迟最低
        """
        # 筛选成功且稳定的结果
        stable = [r for r in results if r.success and r.is_stable and r.latency_ms is not None]
        
        if not stable:
            # 如果没有稳定的，退而求其次选择成功的
            successful = [r for r in results if r.success and r.latency_ms is not None]
            if not successful:
                return None
            return min(successful, key=lambda r: r.latency_ms)
        
        return min(stable, key=lambda r: r.latency_ms)
    
    @staticmethod
    def sort_results(results: List[TestResult]) -> List[TestResult]:
        """
        排序测试结果
        
        排序规则：
        1. 稳定的在前（丢包率 < 20%）
        2. 同等稳定性下，延迟低的在前
        3. 失败的放在最后
        """
        stable = [r for r in results if r.success and r.is_stable]
        unstable = [r for r in results if r.success and not r.is_stable]
        failed = [r for r in results if not r.success]
        
        # 按延迟排序
        stable.sort(key=lambda r: r.latency_ms if r.latency_ms is not None else float('inf'))
        unstable.sort(key=lambda r: r.latency_ms if r.latency_ms is not None else float('inf'))
        
        return stable + unstable + failed
