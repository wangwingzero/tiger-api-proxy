"""
CF Proxy Manager - Comparison Tester
对比测试模块（含丢包率测试）
"""
import socket
import ssl
import time
from typing import List, Optional, Callable, Tuple
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import ComparisonService, ComparisonResult
from .logger import logger


class ComparisonTester:
    """对比测试器（含丢包率测试）"""
    
    def __init__(self, timeout: float = 5.0, test_count: int = 3):
        """
        初始化对比测试器
        
        Args:
            timeout: 单次连接超时时间（秒）
            test_count: 每个服务测试次数（用于计算丢包率）
        """
        self.timeout = timeout
        self.test_count = test_count
        logger.info(f"ComparisonTester 初始化: timeout={timeout}s, test_count={test_count}")
    
    def _test_single_https(self, url: str) -> Optional[float]:
        """
        单次 HTTPS 连接测试
        
        Returns:
            成功返回延迟(ms)，失败返回 None
        """
        sock = None
        ssl_sock = None
        try:
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or 443
            
            if not host:
                logger.debug(f"  无效URL，无法解析主机名: {url}")
                return None
            
            logger.debug(f"  连接 {host}:{port}...")
            start_time = time.perf_counter()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((host, port))
            
            context = ssl.create_default_context()
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            logger.debug(f"  连接成功: {latency_ms:.2f}ms")
            return round(latency_ms, 2)
        except socket.timeout as e:
            logger.debug(f"  连接超时: {host}:{port} - {e}")
            return None
        except socket.error as e:
            logger.debug(f"  Socket错误: {host}:{port} - {e}")
            return None
        except ssl.SSLError as e:
            logger.debug(f"  SSL错误: {host}:{port} - {e}")
            return None
        except OSError as e:
            logger.debug(f"  OS错误: {host}:{port} - {e}")
            return None
        except Exception as e:
            logger.debug(f"  未知错误: {host}:{port} - {type(e).__name__}: {e}")
            return None
        finally:
            if ssl_sock:
                try:
                    ssl_sock.close()
                except Exception:
                    pass
            elif sock:
                try:
                    sock.close()
                except Exception:
                    pass
    
    def _test_single_via_ip(self, domain: str, ip: str, port: int = 443) -> Optional[float]:
        """
        单次通过指定IP的连接测试
        
        Returns:
            成功返回延迟(ms)，失败返回 None
        """
        sock = None
        ssl_sock = None
        try:
            logger.debug(f"  连接 {ip}:{port} (SNI: {domain})...")
            start_time = time.perf_counter()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((ip, port))
            
            context = ssl.create_default_context()
            ssl_sock = context.wrap_socket(sock, server_hostname=domain)
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            logger.debug(f"  连接成功: {latency_ms:.2f}ms")
            return round(latency_ms, 2)
        except socket.timeout as e:
            logger.debug(f"  连接超时: {ip}:{port} - {e}")
            return None
        except socket.error as e:
            logger.debug(f"  Socket错误: {ip}:{port} - {e}")
            return None
        except ssl.SSLError as e:
            logger.debug(f"  SSL错误: {ip}:{port} (SNI: {domain}) - {e}")
            return None
        except OSError as e:
            logger.debug(f"  OS错误: {ip}:{port} - {e}")
            return None
        except Exception as e:
            logger.debug(f"  未知错误: {ip}:{port} - {type(e).__name__}: {e}")
            return None
        finally:
            if ssl_sock:
                try:
                    ssl_sock.close()
                except Exception:
                    pass
            elif sock:
                try:
                    sock.close()
                except Exception:
                    pass
    
    def test_https_latency(self, url: str) -> Tuple[Optional[float], float, str]:
        """
        测试 HTTPS 连接延迟和丢包率
        
        Args:
            url: 完整的 HTTPS URL
            
        Returns:
            (avg_latency_ms, packet_loss_pct, error_message)
        """
        logger.debug(f"测试 HTTPS: {url}")
        
        latencies = []
        for i in range(self.test_count):
            latency = self._test_single_https(url)
            if latency is not None:
                latencies.append(latency)
            logger.debug(f"  第{i+1}次: {latency}ms" if latency else f"  第{i+1}次: 失败")
        
        if latencies:
            avg_latency = round(sum(latencies) / len(latencies), 2)
            packet_loss = round((1 - len(latencies) / self.test_count) * 100, 1)
            logger.info(f"测试完成 {url}: 延迟={avg_latency}ms, 丢包={packet_loss}%")
            return avg_latency, packet_loss, ""
        else:
            logger.warning(f"测试失败 {url}: 所有连接均失败")
            return None, 100.0, "连接失败"
    
    def test_via_ip(self, domain: str, ip: str, port: int = 443) -> Tuple[Optional[float], float, str]:
        """
        通过指定 IP 测试域名连接延迟和丢包率
        
        Args:
            domain: 域名（用于 SNI）
            ip: 目标 IP 地址
            port: 端口号
            
        Returns:
            (avg_latency_ms, packet_loss_pct, error_message)
        """
        logger.debug(f"测试 via IP: {domain} -> {ip}:{port}")
        
        latencies = []
        for i in range(self.test_count):
            latency = self._test_single_via_ip(domain, ip, port)
            if latency is not None:
                latencies.append(latency)
            logger.debug(f"  第{i+1}次: {latency}ms" if latency else f"  第{i+1}次: 失败")
        
        if latencies:
            avg_latency = round(sum(latencies) / len(latencies), 2)
            packet_loss = round((1 - len(latencies) / self.test_count) * 100, 1)
            logger.info(f"测试完成 {domain} via {ip}: 延迟={avg_latency}ms, 丢包={packet_loss}%")
            return avg_latency, packet_loss, ""
        else:
            logger.warning(f"测试失败 {domain} via {ip}: 所有连接均失败")
            return None, 100.0, "连接失败"
    
    def run_comparison(
        self,
        user_domain: str,
        optimized_ip: Optional[str],
        services: List[ComparisonService],
        callback: Optional[Callable[[int, int, ComparisonResult], None]] = None
    ) -> List[ComparisonResult]:
        """
        运行完整对比测试
        
        每个服务都测试直连和优选IP两种方式（如果提供了优选IP）
        """
        logger.info(f"开始对比测试: user_domain={user_domain}, optimized_ip={optimized_ip}")
        logger.info(f"对比服务数量: {len(services)}")
        
        results: List[ComparisonResult] = []
        tasks = []
        
        # 准备测试任务
        if user_domain:
            baseline_service = ComparisonService(
                name="我的反代 (直连)",
                url=f"https://{user_domain}",
                description="直连测试"
            )
            tasks.append(('baseline', baseline_service, None, user_domain))
        
        if user_domain and optimized_ip:
            optimized_service = ComparisonService(
                name="我的反代 (优选IP)",
                url=f"https://{user_domain}",
                description=f"通过 {optimized_ip}"
            )
            tasks.append(('optimized', optimized_service, optimized_ip, user_domain))
        
        for service in services:
            tasks.append(('service', service, None, None))
            
            if optimized_ip:
                parsed = urlparse(service.url)
                service_domain = parsed.hostname
                if service_domain:
                    optimized_service = ComparisonService(
                        name=f"{service.name} (优选IP)",
                        url=service.url,
                        description=f"通过 {optimized_ip}"
                    )
                    tasks.append(('service_optimized', optimized_service, optimized_ip, service_domain))
        
        total = len(tasks)
        logger.info(f"总测试任务数: {total}")
        
        if total == 0:
            return results
        
        baseline_latency: Optional[float] = None
        completed = 0
        
        def test_task(task_type: str, service: ComparisonService, ip: Optional[str], domain: Optional[str]) -> ComparisonResult:
            logger.debug(f"执行任务: type={task_type}, service={service.name}, ip={ip}, domain={domain}")
            
            if ip and domain:
                latency, packet_loss, error = self.test_via_ip(domain, ip)
                is_optimized = True
            else:
                latency, packet_loss, error = self.test_https_latency(service.url)
                is_optimized = False
            
            result = ComparisonResult(
                service=service,
                latency_ms=latency,
                success=latency is not None,
                error_message=error,
                is_baseline=(task_type == 'baseline'),
                is_optimized=is_optimized,
                packet_loss=packet_loss
            )
            
            logger.debug(f"任务完成: {service.name} -> latency={latency}, packet_loss={packet_loss}%, success={result.success}")
            return result
        
        # 并行执行测试
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_task = {
                executor.submit(test_task, t[0], t[1], t[2], t[3]): t
                for t in tasks
            }
            
            for future in as_completed(future_to_task):
                result = future.result()
                results.append(result)
                
                if result.is_baseline and result.success:
                    baseline_latency = result.latency_ms
                
                completed += 1
                if callback:
                    callback(completed, total, result)
        
        # 计算提升百分比
        if baseline_latency is not None and baseline_latency > 0:
            for result in results:
                if result.success and result.latency_ms is not None and not result.is_baseline:
                    result.improvement_pct = self.calculate_improvement(
                        baseline_latency, result.latency_ms
                    )
        
        sorted_results = self.sort_results(results)
        logger.info(f"对比测试完成，共 {len(sorted_results)} 个结果")
        return sorted_results
    
    @staticmethod
    def calculate_improvement(baseline_ms: float, test_ms: float) -> float:
        if baseline_ms <= 0:
            return 0.0
        return round(((baseline_ms - test_ms) / baseline_ms) * 100, 1)
    
    @staticmethod
    def sort_results(results: List[ComparisonResult]) -> List[ComparisonResult]:
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        successful.sort(key=lambda r: r.latency_ms if r.latency_ms is not None else float('inf'))
        return successful + failed
    
    @staticmethod
    def get_best_result(results: List[ComparisonResult]) -> Optional[ComparisonResult]:
        successful = [r for r in results if r.success and r.latency_ms is not None]
        if not successful:
            return None
        return min(successful, key=lambda r: r.latency_ms)
