"""
Theme 模块属性测试
Feature: customtkinter-ui, Property 1: Latency color mapping is consistent
Validates: Requirements 3.1, 3.2, 3.3, 3.4
"""
import pytest
from hypothesis import given, strategies as st, settings

from cf_proxy_manager.components.theme import AppTheme


class TestLatencyColorMapping:
    """
    Property 1: Latency color mapping is consistent
    
    For any latency value (including None), get_latency_color SHALL return:
    - Green (#28a745) for latency < 100ms
    - Orange (#fd7e14) for 100ms ≤ latency < 300ms
    - Red (#dc3545) for latency ≥ 300ms
    - Gray (#6c757d) for None (pending/failed)
    """
    
    @given(st.integers(min_value=0, max_value=99))
    @settings(max_examples=100)
    def test_fast_latency_returns_green(self, latency_ms: int):
        """延迟 < 100ms 应返回绿色"""
        color = AppTheme.get_latency_color(latency_ms)
        assert color == AppTheme.COLORS["success"], \
            f"Latency {latency_ms}ms should return green, got {color}"
    
    @given(st.integers(min_value=100, max_value=299))
    @settings(max_examples=100)
    def test_medium_latency_returns_orange(self, latency_ms: int):
        """100ms ≤ 延迟 < 300ms 应返回橙色"""
        color = AppTheme.get_latency_color(latency_ms)
        assert color == AppTheme.COLORS["warning"], \
            f"Latency {latency_ms}ms should return orange, got {color}"
    
    @given(st.integers(min_value=300, max_value=10000))
    @settings(max_examples=100)
    def test_slow_latency_returns_red(self, latency_ms: int):
        """延迟 ≥ 300ms 应返回红色"""
        color = AppTheme.get_latency_color(latency_ms)
        assert color == AppTheme.COLORS["danger"], \
            f"Latency {latency_ms}ms should return red, got {color}"
    
    def test_none_latency_returns_gray(self):
        """None 延迟应返回灰色"""
        color = AppTheme.get_latency_color(None)
        assert color == AppTheme.COLORS["muted"], \
            f"None latency should return gray, got {color}"
    
    # 边界值测试
    def test_boundary_99ms(self):
        """边界值 99ms 应返回绿色"""
        assert AppTheme.get_latency_color(99) == AppTheme.COLORS["success"]
    
    def test_boundary_100ms(self):
        """边界值 100ms 应返回橙色"""
        assert AppTheme.get_latency_color(100) == AppTheme.COLORS["warning"]
    
    def test_boundary_299ms(self):
        """边界值 299ms 应返回橙色"""
        assert AppTheme.get_latency_color(299) == AppTheme.COLORS["warning"]
    
    def test_boundary_300ms(self):
        """边界值 300ms 应返回红色"""
        assert AppTheme.get_latency_color(300) == AppTheme.COLORS["danger"]


class TestStatusText:
    """测试状态文本生成"""
    
    def test_none_result_returns_pending(self):
        """None 结果应返回待测试状态"""
        text, color = AppTheme.get_status_text(None)
        assert "待测试" in text
        assert color == AppTheme.COLORS["muted"]
    
    def test_success_result_returns_available(self):
        """成功结果应返回可用状态"""
        # 创建模拟成功结果
        class MockResult:
            success = True
            latency_ms = 50
        
        text, color = AppTheme.get_status_text(MockResult())
        assert "可用" in text
        assert color == AppTheme.COLORS["success"]
    
    def test_failed_result_returns_unavailable(self):
        """失败结果应返回不可用状态"""
        class MockResult:
            success = False
            latency_ms = None
        
        text, color = AppTheme.get_status_text(MockResult())
        assert "不可用" in text
        assert color == AppTheme.COLORS["danger"]


class TestThemeConstants:
    """测试主题常量配置"""
    
    def test_latency_thresholds(self):
        """验证延迟阈值配置"""
        assert AppTheme.LATENCY_FAST == 100
        assert AppTheme.LATENCY_MEDIUM == 300
    
    def test_theme_modes(self):
        """验证主题模式配置"""
        assert "dark" in AppTheme.THEME_MODES
        assert "light" in AppTheme.THEME_MODES
        assert "system" in AppTheme.THEME_MODES
    
    def test_colors_defined(self):
        """验证所有颜色已定义"""
        required_colors = ["success", "warning", "danger", "muted", "primary", "best_border"]
        for color_name in required_colors:
            assert color_name in AppTheme.COLORS
            assert AppTheme.COLORS[color_name].startswith("#")
