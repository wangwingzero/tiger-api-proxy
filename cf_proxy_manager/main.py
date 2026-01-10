"""
CF Proxy Manager - Main Entry Point
程序入口
"""
import sys
import ctypes
import os


def is_admin():
    """检查是否以管理员身份运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """请求以管理员身份重新运行"""
    if sys.platform == 'win32':
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            " ".join(sys.argv), 
            None, 
            1
        )


def main():
    """主函数"""
    # 检查管理员权限（可选，用于修改 hosts 文件）
    if not is_admin():
        print("提示: 如需修改 hosts 文件，请以管理员身份运行")
    
    # 导入并启动 CustomTkinter GUI
    from .gui_ctk import CFProxyManagerCTk
    
    app = CFProxyManagerCTk()
    app.run()


if __name__ == "__main__":
    main()
