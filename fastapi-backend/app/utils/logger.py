import logging
import sys
from loguru import logger
from fastapi import FastAPI

class InterceptHandler(logging.Handler):
    """
    拦截标准的 logging 日志，并将其传递给 loguru
    """
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logger():
    # 移除标准库 logging 的处理器
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.INFO)

    # 替换 uvicorn 及其他的 logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # 配置 loguru 的输出格式和终端输出
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": "INFO",
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            },
            # 同步写入到文件，按天按大小轮转归档
            {
                "sink": "logs/app.log",
                "level": "INFO",
                "rotation": "00:00", # 每天午夜轮转
                "retention": "7 days", # 保留7天
                "compression": "zip", # 压缩历史日志
                "encoding": "utf-8"
            }
        ]
    )