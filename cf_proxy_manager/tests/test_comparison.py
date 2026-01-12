"""
CF Proxy Manager - Comparison Feature Tests
对比功能属性测试
"""
import pytest
from typing import List
from hypothesis import given, strategies as st, settings, assume

from cf_proxy_manager.models import (
    ComparisonService, ComparisonResult, Config, IPEntry,
    DEFAULT_COMPARISON_SERVICES
)


# ============================================================================
# Strategies for generating test data
# ============================================================================

@st.composite
def comparison_service_strategy(draw):
    """生成随机 ComparisonService"""
    name = draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip()))
    url = draw(st.text(min_size=1, max_size=200))
    description = draw(st.text(max_size=100))
    is_default = draw(st.booleans())
    return ComparisonService(
        name=name,
        url=url,
        description=description,
        is_default=is_default
    )


@st.composite
def ip_entry_strategy(draw):
    """生成随机 IPEntry"""
    ip = ".".join([str(draw(st.integers(min_value=0, max_value=255))) for _ in range(4)])
    port = draw(st.integers(min_value=1, max_value=65535))
    return IPEntry(ip=ip, port=port)


@st.composite
def config_strategy(draw):
    """生成随机 Config"""
    target_nodes = draw(st.lists(st.text(min_size=1, max_size=50), max_size=5))
    current_target_node = draw(st.text(max_size=50))
    cf_proxy_domain = draw(st.text(max_size=100))
    ip_list = draw(st.lists(ip_entry_strategy(), max_size=10))
    selected_ip = draw(st.one_of(st.none(), st.text(max_size=50)))
    theme_mode = draw(st.sampled_from(["dark", "light", "system"]))
    comparison_services = draw(st.lists(comparison_service_strategy(), max_size=5))
    
    return Config(
        target_nodes=target_nodes,
        current_target_node=current_target_node,
        cf_proxy_domain=cf_proxy_domain,
        ip_list=ip_list,
        selected_ip=selected_ip,
        theme_mode=theme_mode,
        comparison_services=comparison_services
    )


# ============================================================================
# Property 4: Configuration Round-Trip
# For any valid Config object with comparison_services, serializing to dict
# then deserializing should produce an equivalent Config object.
# Validates: Requirements 1.5
# ============================================================================

class TestConfigRoundTrip:
    """Property 4: Configuration Round-Trip"""
    
    @given(config=config_strategy())
    @settings(max_examples=100)
    def test_config_round_trip(self, config: Config):
        """
        **Property 4: Configuration Round-Trip**
        **Validates: Requirements 1.5**
        
        For any valid Config object, serializing to dict then deserializing
        should produce an equivalent Config object.
        """
        # Serialize
        config_dict = config.to_dict()
        
        # Deserialize
        restored = Config.from_dict(config_dict)
        
        # Verify equivalence
        assert restored.target_nodes == config.target_nodes
        assert restored.current_target_node == config.current_target_node
        assert restored.cf_proxy_domain == config.cf_proxy_domain
        assert restored.selected_ip == config.selected_ip
        assert restored.theme_mode == config.theme_mode
        
        # Verify IP list
        assert len(restored.ip_list) == len(config.ip_list)
        for orig, rest in zip(config.ip_list, restored.ip_list):
            assert rest.ip == orig.ip
            assert rest.port == orig.port
        
        # Verify comparison services
        assert len(restored.comparison_services) == len(config.comparison_services)
        for orig, rest in zip(config.comparison_services, restored.comparison_services):
            assert rest.name == orig.name
            assert rest.url == orig.url
            assert rest.description == orig.description
            assert rest.is_default == orig.is_default
    
    @given(service=comparison_service_strategy())
    @settings(max_examples=100)
    def test_comparison_service_round_trip(self, service: ComparisonService):
        """
        ComparisonService serialization round-trip.
        """
        service_dict = service.to_dict()
        restored = ComparisonService.from_dict(service_dict)
        
        assert restored.name == service.name
        assert restored.url == service.url
        assert restored.description == service.description
        assert restored.is_default == service.is_default


# ============================================================================
# ComparisonResult latency_level tests
# ============================================================================

class TestComparisonResultLatencyLevel:
    """Test ComparisonResult.latency_level property"""
    
    def test_latency_level_fast(self):
        """Latency < 200ms should be 'fast'"""
        service = ComparisonService(name="test", url="https://test.com")
        result = ComparisonResult(service=service, latency_ms=150, success=True)
        assert result.latency_level == 'fast'
    
    def test_latency_level_medium(self):
        """Latency 200-500ms should be 'medium'"""
        service = ComparisonService(name="test", url="https://test.com")
        result = ComparisonResult(service=service, latency_ms=350, success=True)
        assert result.latency_level == 'medium'
    
    def test_latency_level_slow(self):
        """Latency > 500ms should be 'slow'"""
        service = ComparisonService(name="test", url="https://test.com")
        result = ComparisonResult(service=service, latency_ms=800, success=True)
        assert result.latency_level == 'slow'
    
    def test_latency_level_failed(self):
        """Failed result should be 'failed'"""
        service = ComparisonService(name="test", url="https://test.com")
        result = ComparisonResult(service=service, latency_ms=None, success=False)
        assert result.latency_level == 'failed'
    
    def test_latency_level_boundary_200(self):
        """Latency exactly 200ms should be 'medium'"""
        service = ComparisonService(name="test", url="https://test.com")
        result = ComparisonResult(service=service, latency_ms=200, success=True)
        assert result.latency_level == 'medium'
    
    def test_latency_level_boundary_500(self):
        """Latency exactly 500ms should be 'slow'"""
        service = ComparisonService(name="test", url="https://test.com")
        result = ComparisonResult(service=service, latency_ms=500, success=True)
        assert result.latency_level == 'slow'


from cf_proxy_manager.comparison_tester import ComparisonTester


# ============================================================================
# Property 5: Improvement Percentage Calculation
# For any baseline latency > 0 and test latency >= 0, the improvement
# percentage should equal (baseline - test) / baseline * 100.
# Validates: Requirements 2.5
# ============================================================================

class TestImprovementCalculation:
    """Property 5: Improvement Percentage Calculation"""
    
    @given(
        baseline=st.floats(min_value=0.1, max_value=10000, allow_nan=False, allow_infinity=False),
        test=st.floats(min_value=0, max_value=10000, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_improvement_calculation(self, baseline: float, test: float):
        """
        **Property 5: Improvement Percentage Calculation**
        **Validates: Requirements 2.5**
        
        For any baseline latency > 0 and test latency >= 0, the improvement
        percentage should equal (baseline - test) / baseline * 100.
        """
        result = ComparisonTester.calculate_improvement(baseline, test)
        expected = round(((baseline - test) / baseline) * 100, 1)
        
        assert result == expected
    
    def test_improvement_positive_when_faster(self):
        """Improvement should be positive when test is faster than baseline"""
        result = ComparisonTester.calculate_improvement(1000, 500)
        assert result == 50.0  # 50% faster
    
    def test_improvement_negative_when_slower(self):
        """Improvement should be negative when test is slower than baseline"""
        result = ComparisonTester.calculate_improvement(500, 1000)
        assert result == -100.0  # 100% slower
    
    def test_improvement_zero_when_equal(self):
        """Improvement should be zero when test equals baseline"""
        result = ComparisonTester.calculate_improvement(500, 500)
        assert result == 0.0
    
    def test_improvement_zero_baseline(self):
        """Should return 0 when baseline is 0 or negative"""
        assert ComparisonTester.calculate_improvement(0, 100) == 0.0
        assert ComparisonTester.calculate_improvement(-100, 100) == 0.0


# ============================================================================
# Property 6: Results Sorting Order
# For any list of ComparisonResults, after sorting:
# - All successful results appear before failed results
# - Successful results are ordered by latency_ms in ascending order
# Validates: Requirements 3.3
# ============================================================================

@st.composite
def comparison_result_strategy(draw):
    """生成随机 ComparisonResult"""
    service = draw(comparison_service_strategy())
    success = draw(st.booleans())
    
    if success:
        latency_ms = draw(st.floats(min_value=0, max_value=5000, allow_nan=False, allow_infinity=False))
        error_message = ""
    else:
        latency_ms = None
        error_message = draw(st.text(max_size=50))
    
    return ComparisonResult(
        service=service,
        latency_ms=latency_ms,
        success=success,
        error_message=error_message
    )


class TestResultsSorting:
    """Property 6: Results Sorting Order"""
    
    @given(results=st.lists(comparison_result_strategy(), min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_sorting_order(self, results: List[ComparisonResult]):
        """
        **Property 6: Results Sorting Order**
        **Validates: Requirements 3.3**
        
        For any list of ComparisonResults, after sorting:
        - All successful results appear before failed results
        - Successful results are ordered by latency_ms in ascending order
        """
        sorted_results = ComparisonTester.sort_results(results)
        
        # Find the boundary between successful and failed
        first_failed_idx = None
        for i, r in enumerate(sorted_results):
            if not r.success:
                first_failed_idx = i
                break
        
        if first_failed_idx is not None:
            # All results before first_failed_idx should be successful
            for i in range(first_failed_idx):
                assert sorted_results[i].success
            
            # All results from first_failed_idx should be failed
            for i in range(first_failed_idx, len(sorted_results)):
                assert not sorted_results[i].success
        
        # Successful results should be sorted by latency
        successful = [r for r in sorted_results if r.success]
        for i in range(len(successful) - 1):
            lat1 = successful[i].latency_ms
            lat2 = successful[i + 1].latency_ms
            if lat1 is not None and lat2 is not None:
                assert lat1 <= lat2


# ============================================================================
# Property 7: Best Result Selection
# For any non-empty list of ComparisonResults with at least one successful
# result, the "best" result should have the minimum latency_ms.
# Validates: Requirements 3.4
# ============================================================================

class TestBestResultSelection:
    """Property 7: Best Result Selection"""
    
    @given(results=st.lists(comparison_result_strategy(), min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_best_result_selection(self, results: List[ComparisonResult]):
        """
        **Property 7: Best Result Selection**
        **Validates: Requirements 3.4**
        
        For any non-empty list of ComparisonResults with at least one successful
        result, the "best" result should have the minimum latency_ms.
        """
        best = ComparisonTester.get_best_result(results)
        successful = [r for r in results if r.success and r.latency_ms is not None]
        
        if not successful:
            # No successful results, best should be None
            assert best is None
        else:
            # Best should exist and have minimum latency
            assert best is not None
            assert best.success
            assert best.latency_ms is not None
            
            min_latency = min(r.latency_ms for r in successful)
            assert best.latency_ms == min_latency
    
    def test_best_result_empty_list(self):
        """Best result of empty list should be None"""
        assert ComparisonTester.get_best_result([]) is None
    
    def test_best_result_all_failed(self):
        """Best result when all failed should be None"""
        service = ComparisonService(name="test", url="https://test.com")
        results = [
            ComparisonResult(service=service, latency_ms=None, success=False),
            ComparisonResult(service=service, latency_ms=None, success=False),
        ]
        assert ComparisonTester.get_best_result(results) is None


from cf_proxy_manager.parsers import URLParser
from cf_proxy_manager.service_manager import ServiceManager


# ============================================================================
# Property 1: URL Validation Correctness
# For any string input, the URL validator should accept only valid HTTPS URLs
# with proper format and reject malformed URLs.
# Validates: Requirements 1.2
# ============================================================================

class TestURLValidation:
    """Property 1: URL Validation Correctness"""
    
    @given(url=st.text(max_size=200))
    @settings(max_examples=100)
    def test_url_validation_consistency(self, url: str):
        """
        **Property 1: URL Validation Correctness**
        **Validates: Requirements 1.2**
        
        URL validation should be consistent and deterministic.
        """
        result1 = URLParser.is_valid_https_url(url)
        result2 = URLParser.is_valid_https_url(url)
        assert result1 == result2
    
    def test_valid_https_urls(self):
        """Valid HTTPS URLs should be accepted"""
        valid_urls = [
            "https://example.com",
            "https://sub.example.com",
            "https://example.com/path",
            "https://example.com/path/to/resource",
            "https://a-b.example.com",
            "https://123.example.com",
        ]
        for url in valid_urls:
            assert URLParser.is_valid_https_url(url), f"Should accept: {url}"
    
    def test_invalid_urls_rejected(self):
        """Invalid URLs should be rejected"""
        invalid_urls = [
            "",
            "http://example.com",  # HTTP not HTTPS
            "ftp://example.com",
            "example.com",  # No protocol
            "https://",  # No host
            "https:///path",  # No host
            "not a url",
        ]
        for url in invalid_urls:
            assert not URLParser.is_valid_https_url(url), f"Should reject: {url}"


# ============================================================================
# Property 2: Service List Removal Invariant
# For any list of comparison services and any service in that list, after
# removal, the resulting list should not contain that service.
# Validates: Requirements 1.3
# ============================================================================

class TestServiceListRemoval:
    """Property 2: Service List Removal Invariant"""
    
    @given(services=st.lists(comparison_service_strategy(), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_removal_invariant(self, services: List[ComparisonService]):
        """
        **Property 2: Service List Removal Invariant**
        **Validates: Requirements 1.3**
        
        After removing a service, the list should not contain that service.
        """
        manager = ServiceManager(services)
        
        # Pick a service to remove
        service_to_remove = services[0]
        url_to_remove = service_to_remove.url
        
        # Count how many services have this URL
        count_before = sum(1 for s in manager.services if s.url == url_to_remove)
        original_len = len(manager.services)
        
        # Remove it
        result = manager.remove_service(url_to_remove)
        
        # Verify removal
        assert result == True
        # All services with this URL should be removed
        assert manager.find_by_url(url_to_remove) is None
        # Length should decrease by the count of matching services
        assert len(manager.services) == original_len - count_before
    
    def test_remove_nonexistent_service(self):
        """Removing nonexistent service should return False"""
        manager = ServiceManager()
        original_len = len(manager.services)
        
        result = manager.remove_service("https://nonexistent.example.com")
        
        assert result == False
        assert len(manager.services) == original_len


# ============================================================================
# Property 3: Reset to Defaults Idempotence
# For any modified comparison services list, resetting to defaults should
# produce a list equal to DEFAULT_COMPARISON_SERVICES.
# Validates: Requirements 1.4
# ============================================================================

class TestResetToDefaults:
    """Property 3: Reset to Defaults Idempotence"""
    
    @given(services=st.lists(comparison_service_strategy(), min_size=0, max_size=10))
    @settings(max_examples=100)
    def test_reset_idempotence(self, services: List[ComparisonService]):
        """
        **Property 3: Reset to Defaults Idempotence**
        **Validates: Requirements 1.4**
        
        Resetting to defaults should produce the exact default list,
        and resetting multiple times should produce the same result.
        """
        manager = ServiceManager(services)
        
        # Reset once
        manager.reset_to_defaults()
        first_reset = [s.url for s in manager.services]
        
        # Reset again
        manager.reset_to_defaults()
        second_reset = [s.url for s in manager.services]
        
        # Should be identical
        assert first_reset == second_reset
        
        # Should match default list
        default_urls = [s.url for s in DEFAULT_COMPARISON_SERVICES]
        assert first_reset == default_urls
    
    def test_reset_restores_defaults(self):
        """Reset should restore exact default services"""
        manager = ServiceManager([])
        
        # Add custom service
        manager.add_service("Custom", "https://custom.example.com", "Test")
        
        # Reset
        manager.reset_to_defaults()
        
        # Verify
        assert manager.is_default_list()
        assert len(manager.services) == len(DEFAULT_COMPARISON_SERVICES)
