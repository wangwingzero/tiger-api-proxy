"""
Property-based tests for SpeedTester
Feature: cf-proxy-manager
Property 3: Best IP Selection Correctness
Property 4: Failed IP Exclusion
Property 5: Test Results Sorting
Validates: Requirements 4.5, 4.6, 4.7
"""
from hypothesis import given, strategies as st, settings, HealthCheck, assume

from cf_proxy_manager.models import IPEntry, TestResult
from cf_proxy_manager.speed_tester import SpeedTester


# Strategies
ip_octet = st.integers(min_value=0, max_value=255)
ip_strategy = st.tuples(ip_octet, ip_octet, ip_octet, ip_octet).map(
    lambda t: f"{t[0]}.{t[1]}.{t[2]}.{t[3]}"
)

port_strategy = st.integers(min_value=1, max_value=65535)

ip_entry_strategy = st.builds(
    IPEntry,
    ip=ip_strategy,
    port=port_strategy
)

# Test result strategies
successful_result_strategy = st.builds(
    TestResult,
    ip_entry=ip_entry_strategy,
    latency_ms=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False),
    success=st.just(True),
    error_message=st.just("")
)

failed_result_strategy = st.builds(
    TestResult,
    ip_entry=ip_entry_strategy,
    latency_ms=st.none(),
    success=st.just(False),
    error_message=st.text(min_size=1, max_size=50)
)

test_result_strategy = successful_result_strategy | failed_result_strategy


class TestSpeedTesterProperties:
    """Property-based tests for SpeedTester"""
    
    @given(results=st.lists(successful_result_strategy, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_best_ip_is_minimum_latency(self, results):
        """
        Property 3: Best IP Selection Correctness
        For any list of successful results, get_best_ip should return
        the result with minimum latency.
        Validates: Requirements 4.5
        """
        best = SpeedTester.get_best_ip(results)
        
        assert best is not None
        assert best.success is True
        
        # Verify it has the minimum latency
        min_latency = min(r.latency_ms for r in results)
        assert best.latency_ms == min_latency
    
    @given(results=st.lists(failed_result_strategy, min_size=1, max_size=10))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_no_best_ip_when_all_failed(self, results):
        """
        Property 4: Failed IP Exclusion
        When all results are failed, get_best_ip should return None.
        Validates: Requirements 4.6
        """
        best = SpeedTester.get_best_ip(results)
        assert best is None
    
    @given(
        successful=st.lists(successful_result_strategy, min_size=1, max_size=10),
        failed=st.lists(failed_result_strategy, min_size=1, max_size=10)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_best_ip_excludes_failed(self, successful, failed):
        """
        Property 4: Failed IP Exclusion
        get_best_ip should never return a failed result.
        Validates: Requirements 4.6
        """
        mixed_results = successful + failed
        
        best = SpeedTester.get_best_ip(mixed_results)
        
        assert best is not None
        assert best.success is True
        assert best in successful
    
    @given(results=st.lists(test_result_strategy, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_sort_results_ordering(self, results):
        """
        Property 5: Test Results Sorting
        After sorting, successful results should come before failed,
        and successful results should be ordered by ascending latency.
        Validates: Requirements 4.7
        """
        sorted_results = SpeedTester.sort_results(results)
        
        # Same length
        assert len(sorted_results) == len(results)
        
        # Find where failed results start
        first_failed_idx = None
        for i, r in enumerate(sorted_results):
            if not r.success:
                first_failed_idx = i
                break
        
        if first_failed_idx is not None:
            # All results before first_failed_idx should be successful
            for i in range(first_failed_idx):
                assert sorted_results[i].success is True
            
            # All results from first_failed_idx should be failed
            for i in range(first_failed_idx, len(sorted_results)):
                assert sorted_results[i].success is False
        
        # Successful results should be sorted by latency
        successful = [r for r in sorted_results if r.success]
        for i in range(len(successful) - 1):
            assert successful[i].latency_ms <= successful[i + 1].latency_ms
    
    @given(results=st.lists(successful_result_strategy, min_size=2, max_size=10))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_sort_preserves_all_results(self, results):
        """
        Sorting should preserve all results (no loss).
        """
        sorted_results = SpeedTester.sort_results(results)
        
        # Same IPs should be present
        original_ips = {r.ip_entry.ip for r in results}
        sorted_ips = {r.ip_entry.ip for r in sorted_results}
        
        assert original_ips == sorted_ips
    
    def test_empty_results(self):
        """Test edge case: empty results list"""
        assert SpeedTester.get_best_ip([]) is None
        assert SpeedTester.sort_results([]) == []
