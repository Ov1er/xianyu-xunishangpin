"""
请求限速器
控制请求频率，避免触发反爬机制
"""

import time
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """请求限速器"""
    
    def __init__(
        self,
        min_delay: float = 2.0,
        max_delay: float = 5.0,
        last_request_time: Optional[float] = None
    ):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = last_request_time or time.time()
    
    def wait(self, custom_delay: Optional[float] = None):
        if custom_delay is not None:
            delay = custom_delay
        else:
            delay = random.uniform(self.min_delay, self.max_delay)
        
        logger.debug(f"等待 {delay:.2f} 秒...")
        time.sleep(delay)
        self.last_request_time = time.time()
    
    def adaptive_wait(
        self,
        base_delay: float = 3.0,
        failure_count: int = 0,
        max_backoff: float = 30.0
    ):
        if failure_count == 0:
            delay = base_delay
        else:
            delay = min(base_delay * (2 ** failure_count), max_backoff)
        
        delay = delay + random.uniform(0, delay * 0.2)
        logger.info(f"自适应等待 {delay:.2f} 秒 (失败次数: {failure_count})")
        time.sleep(delay)
        self.last_request_time = time.time()
    
    @property
    def elapsed_since_last_request(self) -> float:
        return time.time() - self.last_request_time
    
    def reset(self):
        self.last_request_time = time.time()
        logger.debug("限速器已重置")


CONSERVATIVE_LIMITER = RateLimiter(min_delay=5.0, max_delay=10.0)
NORMAL_LIMITER = RateLimiter(min_delay=2.0, max_delay=5.0)
AGGRESSIVE_LIMITER = RateLimiter(min_delay=0.5, max_delay=2.0)
