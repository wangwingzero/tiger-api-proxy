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
    """请求以管理员身份重新运行
    
    Returns:
        True 如果成功启动提权进程，False 如果用户取消或失败
    """
    if sys.platform == 'win32':
        try:
            # 获取当前脚本路径
            if getattr(sys, 'frozen', False):
                # PyInstaller 打包后的 exe
                script = sys.executable
                params = " ".join(sys.argv[1:])
            else:
                # 普通 Python 脚本
                script = sys.executable
                params = f'"{sys.argv[0]}"'
                if len(sys.argv) > 1:
                    params += " " + " ".join(sys.argv[1:])
            
            # 请求管理员权限运行
            result = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                script,
                params,
                None,
                1  # SW_SHOWNORMAL
            )
            # ShellExecuteW 返回值 > 32 表示成功
            return result > 32
        except Exception as e:
            print(f"请求管理员权限失败: {e}")
            return False
    return False


def main():
    """主函数"""
    # 检查管理员权限
    if not is_admin():
        print("检测到非管理员权限，正在请求提权...")
        if run_as_admin():
            # 成功启动了提权进程，退出当前进程
            sys.exit(0)
        else:
            # 用户取消或提权失败，继续以普通权限运行
            print("提示: 以普通权限运行，修改 hosts 文件功能将不可用")
    
    # 导入并启动 CustomTkinter GUI
    from .gui_ctk import CFProxyManagerCTk
    
    app = CFProxyManagerCTk()
    app.run()


if __name__ == "__main__":
    main()
