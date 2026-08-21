"""Tests for Rate Limiting and Brute-Force Protection."""

import pytest
from app.security.rate_limiter import SlidingWindowRateLimiter


def test_sliding_window_rate_limiter_allows_under_limit():
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=10, name="TestLimiter")
    
    # First 3 requests should succeed
    allowed1, _ = limiter.check_and_record("user1")
    allowed2, _ = limiter.check_and_record("user1")
    allowed3, _ = limiter.check_and_record("user1")
    
    assert allowed1 is True
    assert allowed2 is True
    assert allowed3 is True


def test_sliding_window_rate_limiter_blocks_on_breach():
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=10, name="TestLimiter")
    
    limiter.check_and_record("user2")
    limiter.check_and_record("user2")
    
    # 3rd request should be blocked
    allowed, retry_after = limiter.check_and_record("user2")
    assert allowed is False
    assert retry_after > 0


def test_sliding_window_lockout_mechanism():
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=10, name="TestLimiter")
    
    limiter.check_and_record("user3", lockout_on_breach=60)
    limiter.check_and_record("user3", lockout_on_breach=60)
    
    # Breaching with lockout_on_breach triggers 60s lockout
    allowed, retry_after = limiter.check_and_record("user3", lockout_on_breach=60)
    assert allowed is False
    assert retry_after > 0
    
    is_locked, rem = limiter.is_locked_out("user3")
    assert is_locked is True
    assert rem > 0


def test_sliding_window_reset():
    limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=10, name="TestLimiter")
    
    limiter.check_and_record("user4")
    # Blocked
    allowed, _ = limiter.check_and_record("user4")
    assert allowed is False
    
    # Reset
    limiter.reset("user4")
    
    # Allowed again
    allowed_after, _ = limiter.check_and_record("user4")
    assert allowed_after is True
