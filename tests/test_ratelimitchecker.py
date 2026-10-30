# test_ratelimitchecker.py

import BeeGhost.models.ratelimitchecker as ratelimitchecker
from BeeGhost.models.ratelimitchecker import RateLimitChecker

def test_max_requests():
    rlm = RateLimitChecker(max_requests=0)
    assert rlm.is_allowed() == False

def test_sleep_time_0():
    rlm = RateLimitChecker()
    assert rlm.get_sleep_time() == 0.0

def test_sleep_time(monkeypatch):
    
    current_time = [1000.0]
    
    monkeypatch.setattr(
        ratelimitchecker.time,
        "time",
        lambda: current_time[0]
    )
    
    rlm = RateLimitChecker(
        max_requests=1,
        window_seconds=60
    )
    
    rlm.request_history.append(1000.0)
    
    current_time[0] = 1020.0
    
    assert rlm.get_sleep_time() == 40.0
    
def test_sleep_time_after_window_expires(monkeypatch):
    
    current_time = [1000.0]
    
    monkeypatch.setattr(
        ratelimitchecker.time,
        "time",
        lambda: current_time[0]
    )
    
    rlm = RateLimitChecker(
        max_requests=1,
        window_seconds=60
    )
    
    rlm.request_history.append(1000.0)
    
    current_time[0] = 1060.0
    
    assert rlm.get_sleep_time() == 0.0
    