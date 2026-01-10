"""
CF Proxy Manager - Admin Helper
管理员权限辅助模块
"""
import sys
import ctypes
import os
from tkinter import messagebox
from typing import Optional


class AdminHelper:
    """管理员权限辅助类"""
    
    @staticmethod
    def is_admin() -> bool:
        """
        检查当前是否以管理员身份运行
        
        Returns:
            True 如果是管理员，否则 False
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    @staticmethod
    def restart_as_admin() -> bool:
        """
        以管理员身份重新启动程序
        
        Returns:
            True 如果成功启动，否则 False
        """
        if sys.platform != 'win32':
            return False
        
        try:
            # 获取当前脚本路径
            if getattr(sys, 'frozen', False):
                # 打包后的 exe
                script = sys.executable
                params = " ".join(sys.argv[1:])
            else:
                # 开发环境
                script = sys.executable
                params = " ".join(['"' + sys.argv[0] + '"'] + sys.argv[1:])
            
            # 使用 ShellExecute 以管理员身份运行
            result = ctypes.windll.shell32.ShellExecuteW(
                None,           # hwnd
                "runas",        # 操作 (以管理员身份运行)
                script,         # 程序路径
                params,         # 参数
                None,           # 工作目录
                1               # 显示窗口
            )
            
            # ShellExecuteW 返回值 > 32 表示成功
            if result > 32:
                sys.exit(0)
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def request_admin_if_needed(action_name: str = "此操作", 
                                 parent=None) -> bool:
        """
        如果需要管理员权限，提示用户并请求重启
        
        Args:
            action_name: 操作名称，用于显示在对话框中
            parent: 父窗口
            
        Returns:
            True 如果已有权限
            False 如果用户取消或重启失败
        """
        if AdminHelper.is_admin():
            return True
        
        result = messagebox.askyesno(
            "需要管理员权限",
            f"执行「{action_name}」需要管理员权限。\n\n"
            "是否以管理员身份重新启动程序？",
            parent=parent
        )
        
        if result:
            if AdminHelper.restart_as_admin():
                return True
            else:
                messagebox.showerror(
                    "启动失败",
                    "无法以管理员身份重新启动程序。\n"
                    "请手动右键点击程序，选择「以管理员身份运行」。",
                    parent=parent
                )
        
        return False
    
    @staticmethod
    def get_status_text() -> str:
        """
        获取当前权限状态文本
        
        Returns:
            状态文本
        """
        if AdminHelper.is_admin():
            return "✅ 管理员模式"
        else:
            return "⚠️ 普通模式"
    
    @staticmethod
    def get_status_color() -> str:
        """
        获取当前权限状态颜色
        
        Returns:
            颜色代码
        """
        if AdminHelper.is_admin():
            return "#34C759"  # iOS 绿色
        else:
            return "#FF9500"  # iOS 橙色
