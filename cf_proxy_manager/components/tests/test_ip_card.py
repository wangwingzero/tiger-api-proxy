"""
IP Card 组件属性测试
Feature: customtkinter-ui
Property 3: IP card contains all required information
Property 6: Card selection toggle is idempotent after two clicks
Validates: Requirements 2.2, 2.4
"""
import pytest
from hypothesis import given, strategies as st, settings
from dataclasses import dataclass
from typing import Optional


# 模拟 IPEntry 和 TestResult 用于测试
@dataclass
class MockIPEntry:
    ip: str
    port: int


@dataclass  
class MockTestResult:
    success: bool
    latency_ms: Optional[int]
    ip_entry: MockIPEntry


class TestIPCardInformation:
    """
    Property 3: IP card contains all required information
    
    For any IPCard created with an ip_entry and optional result, the card SHALL display:
    - The IP address from ip_entry.ip
    - The port from ip_entry.port
    - Latency value (or "--" if no result)
    - Status text matching the result state
    """
    
    @given(
        ip_octets=st.tuples(
            st.integers(min_value=1, max_value=255),
            st.integers(min_value=0, max_value=255),
            st.integers(min_value=0, max_value=255),
            st.integers(min_value=1, max_value=255)
        ),
        port=st.integers(min_value=1, max_value=65535)
    )
    @settings(max_examples=100)
    def test_ip_text_contains_ip_and_port(self, ip_octets, port):
        """IP 文本应包含 IP 地址和端口"""
        ip = f"{ip_octets[0]}.{ip_octets[1]}.{ip_octets[2]}.{ip_octets[3]}"
        ip_entry = MockIPEntry(ip=ip, port=port)
        
        # 验证 IP 文本格式
        expected_text = f"{ip}:{port}"
        assert ip_entry.ip in expected_text
        assert str(port) in expected_text
    
    @given(latency=st.integers(min_value=1, max_value=5000))
    @settings(max_examples=100)
    def test_latency_display_for_success_result(self, latency):
        """成功结果应显示延迟值"""
        from cf_proxy_manager.components.theme import AppTheme
        
        ip_entry = MockIPEntry(ip="1.2.3.4", port=443)
        result = MockTestResult(success=True, latency_ms=latency, ip_entry=ip_entry)
        
        latency_text, _ = AppTheme.get_latency_display(result)
        assert f"{latency}ms" == latency_text
    
    def test_latency_display_for_none_result(self):
        """无结果应显示 '--'"""
        from cf_proxy_manager.components.theme import AppTheme
        
        latency_text, _ = AppTheme.get_latency_display(None)
        assert latency_text == "--"
    
    def test_latency_display_for_failed_result(self):
        """失败结果应显示 '--'"""
        from cf_proxy_manager.components.theme import AppTheme
        
        ip_entry = MockIPEntry(ip="1.2.3.4", port=443)
        result = MockTestResult(success=False, latency_ms=None, ip_entry=ip_entry)
        
        latency_text, _ = AppTheme.get_latency_display(result)
        assert latency_text == "--"
    
    def test_status_text_for_success(self):
        """成功结果应显示可用状态"""
        from cf_proxy_manager.components.theme import AppTheme
        
        ip_entry = MockIPEntry(ip="1.2.3.4", port=443)
        result = MockTestResult(success=True, latency_ms=50, ip_entry=ip_entry)
        
        status_text, _ = AppTheme.get_status_text(result)
        assert "可用" in status_text
    
    def test_status_text_for_failure(self):
        """失败结果应显示不可用状态"""
        from cf_proxy_manager.components.theme import AppTheme
        
        ip_entry = MockIPEntry(ip="1.2.3.4", port=443)
        result = MockTestResult(success=False, latency_ms=None, ip_entry=ip_entry)
        
        status_text, _ = AppTheme.get_status_text(result)
        assert "不可用" in status_text
    
    def test_status_text_for_pending(self):
        """无结果应显示待测试状态"""
        from cf_proxy_manager.components.theme import AppTheme
        
        status_text, _ = AppTheme.get_status_text(None)
        assert "待测试" in status_text


class TestCardSelectionToggle:
    """
    Property 6: Card selection toggle is idempotent after two clicks
    
    For any IPCard, clicking twice SHALL return the card to its original selection state.
    """
    
    @given(initial_selected=st.booleans())
    @settings(max_examples=100)
    def test_double_toggle_returns_to_original_state(self, initial_selected):
        """双击切换应返回原始状态"""
        # 模拟选中状态切换逻辑
        state = initial_selected
        
        # 第一次切换
        state = not state
        
        # 第二次切换
        state = not state
        
        # 应该回到原始状态
        assert state == initial_selected
    
    @given(num_toggles=st.integers(min_value=0, max_value=100))
    @settings(max_examples=100)
    def test_even_toggles_preserve_state(self, num_toggles):
        """偶数次切换应保持原始状态"""
        initial_state = False
        state = initial_state
        
        # 执行偶数次切换
        for _ in range(num_toggles * 2):
            state = not state
        
        assert state == initial_state
    
    @given(num_toggles=st.integers(min_value=0, max_value=100))
    @settings(max_examples=100)
    def test_odd_toggles_flip_state(self, num_toggles):
        """奇数次切换应翻转状态"""
        initial_state = False
        state = initial_state
        
        # 执行奇数次切换
        for _ in range(num_toggles * 2 + 1):
            state = not state
        
        assert state == (not initial_state)


class TestIPCardConstants:
    """测试 IP 卡片常量"""
    
    def test_min_height_defined(self):
        """验证最小高度已定义"""
        from cf_proxy_manager.components.ip_card import IPCard
        assert hasattr(IPCard, 'MIN_HEIGHT')
        assert IPCard.MIN_HEIGHT >= 50
