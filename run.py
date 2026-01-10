"""
CF Proxy Manager - 启动脚本
双击运行此文件启动程序
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cf_proxy_manager.main import main

if __name__ == "__main__":
    main()
