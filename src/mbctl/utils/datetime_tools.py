# 生成一些时间相关的信息
from datetime import datetime


def get_current_iso_datetime():
    """获取当前的时间戳，格式为 YYYY-MM-DD HH:MM:SS"""
    return datetime.now().isoformat(sep=" ", timespec="seconds")
