"""
CF Proxy Manager - Logger
日志模块 - 详细记录每一步操作用于故障排查
"""
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path


def get_app_dir() -> Path:
    """获取应用程序所在目录"""
    # 如果是打包后的 exe，使用 exe 所在目录
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    # 否则使用 run.py 所在目录（项目根目录）
    return Path(__file__).parent.parent


def setup_logger(name: str = "cf_proxy_manager", log_to_file: bool = True) -> logging.Logger:
    """
    设置日志记录器
    
    日志文件保存在项目根目录下的 logs 文件夹中
    
    Args:
        name: 日志记录器名称
        log_to_file: 是否写入文件
        
    Returns:
        配置好的 Logger 对象
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # 详细日志格式（包含文件名、行号、函数名）
    detailed_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d [%(levelname)s] %(filename)s:%(lineno)d %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 简洁日志格式（控制台用）
    simple_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # 控制台输出（简洁格式）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # 文件输出（详细格式）
    if log_to_file:
        try:
            # 日志目录在项目根目录下
            app_dir = get_app_dir()
            log_dir = app_dir / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 日志文件名包含日期
            log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
            
            # 记录启动信息
            logger.info("=" * 60)
            logger.info(f"应用启动 - 日志文件: {log_file}")
            logger.info(f"Python 版本: {sys.version}")
            logger.info(f"应用目录: {app_dir}")
            logger.info("=" * 60)
        except Exception as e:
            logger.warning(f"无法创建日志文件: {e}")
    
    return logger


def log_exception(logger: logging.Logger, msg: str = "发生异常"):
    """
    记录异常的详细信息
    
    Args:
        logger: Logger 对象
        msg: 异常描述
    """
    logger.error(f"{msg}:\n{traceback.format_exc()}")


# 全局日志实例
logger = setup_logger()
