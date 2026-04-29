"""
通用辅助函数库
提供日志、错误处理、工具函数等通用能力
"""

import json
import logging
import functools
import random
import string
from datetime import datetime
from typing import Callable, Any, Optional


# ========== 日志配置 ==========
def setup_logging(log_file: str = 'app.log', level: int = logging.INFO):
    """
    配置日志系统
    
    参数:
        log_file: 日志文件路径
        level: 日志级别
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


logger = logging.getLogger(__name__)


# ========== 装饰器 ==========

def handle_errors(func: Callable = None, *, error_message: str = None):
    """
    错误处理装饰器
    统一捕获异常并提供友好的错误提示
    
    使用方式:
        @handle_errors
        def my_function(): ...
        
        或带自定义消息:
        @handle_errors(error_message="操作失败")
        def my_function(): ...
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return fn(*args, **kwargs)
            except FileNotFoundError as e:
                msg = error_message or "⚠️ 所需文件不存在，请检查数据目录"
                logger.error(f"文件未找到 [{fn.__name__}]: {e}")
                raise Exception(msg)
            except json.JSONDecodeError as e:
                msg = error_message or "⚠️ 数据文件格式错误，请重新初始化"
                logger.error(f"JSON解析错误 [{fn.__name__}]: {e}")
                raise Exception(msg)
            except PermissionError as e:
                msg = error_message or "⚠️ 文件权限不足，请检查目录权限"
                logger.error(f"权限错误 [{fn.__name__}]: {e}")
                raise Exception(msg)
            except KeyError as e:
                msg = error_message or f"⚠️ 缺少必要的数据字段: {e}"
                logger.error(f"键错误 [{fn.__name__}]: {e}")
                raise Exception(msg)
            except ValueError as e:
                msg = error_message or f"⚠️ 参数值无效: {e}"
                logger.error(f"值错误 [{fn.__name__}]: {e}")
                raise Exception(msg)
            except Exception as e:
                msg = error_message or f"❌ 操作失败: {str(e)}"
                logger.error(f"未知错误 [{fn.__name__}]: {e}", exc_info=True)
                raise Exception(msg)
        return wrapper
    
    if func is not None:
        return decorator(func)
    return decorator


def log_execution_time(func: Callable) -> Callable:
    """
    执行时间记录装饰器
    记录函数执行耗时，用于性能监控
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"⏱️ {func.__name__} 执行耗时: {duration:.3f}秒")
        return result
    return wrapper


# ========== 工具函数 ==========

def safe_division(a: float, b: float, default: float = 0.0) -> float:
    """
    安全除法，避免除零错误
    
    参数:
        a: 被除数
        b: 除数
        default: 除数为零时的默认返回值
        
    返回:
        除法结果或默认值
    """
    try:
        if b == 0:
            return default
        return a / b
    except (TypeError, ZeroDivisionError):
        return default


def format_file_size(size_bytes: int) -> str:
    """
    将字节转换为人类可读的文件大小
    
    参数:
        size_bytes: 文件大小（字节）
        
    返回:
        格式化后的字符串（如"256MB"、"1.5GB"）
    """
    if size_bytes == 0:
        return "0B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)}{units[unit_index]}"
    elif size < 10:
        return f"{size:.2f}{units[unit_index]}"
    elif size < 100:
        return f"{size:.1f}{units[unit_index]}"
    else:
        return f"{int(size)}{units[unit_index]}"


def generate_unique_id(prefix: str = "", length: int = 8) -> str:
    """
    生成唯一标识符
    
    参数:
        prefix: ID前缀（如'KY','OT','ER','NT'）
        length: 随机部分长度
                
    返回:
        唯一ID字符串
    """
    timestamp_part = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}{timestamp_part}{random_part}" if prefix else f"{timestamp_part}{random_part}"


def get_timestamp(format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    获取当前时间戳字符串
    
    参数:
        format_str: 时间格式
        
    返回:
        格式化的时间字符串
    """
    return datetime.now().strftime(format_str)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    参数:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
        
    返回:
        截断后的文本
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, top_n: int = 5) -> list:
    """
    从文本中提取关键词（简单实现，基于词频）
    
    参数:
        text: 输入文本
        top_n: 返回前N个关键词
        
    返回:
        关键词列表
    """
    import re
    from collections import Counter
    
    # 简单的分词（中文按字符，英文按单词）
    chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
    english_words = re.findall(r'[a-zA-Z]{3,}', text.lower())
    
    all_tokens = chinese_chars + english_words
    
    # 过滤停用词（简单版）
    stopwords = {'的', '是', '在', '了', '和', '与', '或', '等', 'the', 'a', 'an', 'is', 'are', 'was', 'were'}
    filtered = [t for t in all_tokens if t.lower() not in stopwords and len(t) > 1]
    
    counter = Counter(filtered)
    return [word for word, count in counter.most_common(top_n)]


def calculate_reading_time(text: str, words_per_minute: int = 300) -> str:
    """
    估算文本阅读时间
    
    参数:
        text: 文本内容
        words_per_minute: 每分钟阅读字数
        
    返回:
        阅读时间描述（如"约3分钟"）
    """
    import re
    
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    total_units = chinese_chars + english_words
    
    minutes = total_units / words_per_minute
    
    if minutes < 1:
        seconds = int(minutes * 60)
        return f"约{seconds}秒"
    elif minutes < 60:
        return f"约{int(minutes)}分钟"
    else:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        return f"约{hours}小时{mins分钟}"
