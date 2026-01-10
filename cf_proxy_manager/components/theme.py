"""
CF Proxy Manager - Theme Configuration
应用主题配置模块
"""
from typing import Optional, Tuple


class AppTheme:
    """应用主题配置"""
    
    # 延迟阈值 (毫秒)
    LATENCY_FAST = 100
    LATENCY_MEDIUM = 300
    
    # 颜色定义
    COLORS = {
        "success": "#28a745",     # 绿色 - 快速/成功
        "warning": "#fd7e14",     # 橙色 - 中等
        "danger": "#dc3545",      # 红色 - 慢/失败
        "muted": "#6c757d",       # 灰色 - 待测试
        "primary": "#3b8ed0",     # 蓝色 - 主要操作
        "best_border": "#ffc107", # 金色 - 最佳IP边框
    }
    
    # 字体配置
    FONT_MONO = ("Consolas", 13)
    FONT_DEFAULT = ("Segoe UI", 12)
    FONT_SMALL = ("Segoe UI", 10)
    FONT_BOLD = ("Segoe UI", 12, "bold")
    
    # 主题模式
    THEME_MODES = ["dark", "light", "system"]
    THEME_LABELS = {
        "dark": "深色",
        "light": "浅色", 
        "system": "跟随系统"
    }
    
    @staticmethod
    def get_latency_color(latency_ms: Optional[int]) -> str:
        """
        根据延迟返回对应颜色
        
        Args:
            latency_ms: 延迟毫秒数，None 表示待测试或失败
            
        Returns:
            颜色十六进制字符串
        """
        if latency_ms is None:
            return AppTheme.COLORS["muted"]
        if latency_ms < AppTheme.LATENCY_FAST:
            return AppTheme.COLORS["success"]
        if latency_ms < AppTheme.LATENCY_MEDIUM:
            return AppTheme.COLORS["warning"]
        return AppTheme.COLORS["danger"]
    
    @staticmethod
    def get_status_text(result) -> Tuple[str, str]:
        """
        根据测试结果返回状态文本和颜色
        
        Args:
            result: TestResult 对象或 None
            
        Returns:
            (状态文本, 颜色) 元组
        """
        if result is None:
            return ("⏳ 待测试", AppTheme.COLORS["muted"])
        if result.success:
            return ("✓ 可用", AppTheme.COLORS["success"])
        return ("✗ 不可用", AppTheme.COLORS["danger"])
    
    @staticmethod
    def get_latency_display(result) -> Tuple[str, str]:
        """
        获取延迟显示文本和颜色
        
        Args:
            result: TestResult 对象或 None
            
        Returns:
            (延迟文本, 颜色) 元组
        """
        if result is None:
            return ("--", AppTheme.COLORS["muted"])
        if result.success:
            return (f"{result.latency_ms}ms", 
                    AppTheme.get_latency_color(result.latency_ms))
        return ("--", AppTheme.COLORS["danger"])
