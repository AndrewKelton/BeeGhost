import time
from collections import deque
import logging

logging.basicConfig(
    level=logging.INFO,
    style="{",
    format="\n[{asctime}] {message}\n",
    datefmt="%H:%M:%S"
)

class RateLimitChecker:
    def __init__(self, max_requests : int = 100, window_seconds: int = 3600):
        """
        :param max_requests: Maximum allowed requests within the window.
        :param window_seconds: The duration of the rolling window in seconds.
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_history = deque()
        
    def is_allowed(self) -> bool:
        """
        Checks if a request can be made right now.
        Decrements/cleans out expired timestamps outside the rolling window.
        
        Returns:
            bool: True if request is allowed, False otherwise.
        """
        current_time = time.time()
        
        while self.request_history and self.request_history[0] <= current_time - self.window_seconds:
            self.request_history.popleft()
        
        if len(self.request_history) < self.max_requests:
            return True
        
        return False
    
    def record_request(self):
        """Logs a request timestamp when a call is successfully made."""
        self.request_history.append(time.time())
        logging.info("Record request added to queue")
        
    def get_sleep_time(self) -> float:
        """
        Calculates how long we need to wait before the next available
        token opens up in the sliding window.
        
        Returns:
            float: max time to wait
        """
        if self.is_allowed():
            return 0.0
        
        current_time = time.time()
        
        # oldest request dictates the wait time
        oldest_request = self.request_history[0]
        wait_time = (oldest_request + self.window_seconds) - current_time
        
        logging.info(f"Rate limited for {wait_time:.2f}s")
        
        return max(0.0, wait_time)
        