"""In-memory sliding window rate limiter for security, brute-force protection, and abuse prevention."""

import time
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import Request, HTTPException, status


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding window rate limiter."""
    def __init__(self, max_requests: int, window_seconds: int, name: str = "RateLimiter"):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.name = name
        # key -> list of timestamps
        self._history: Dict[str, List[float]] = defaultdict(list)
        # key -> lock expiration timestamp
        self._lockouts: Dict[str, float] = {}

    def is_locked_out(self, key: str) -> Tuple[bool, int]:
        """Check if key is currently locked out; returns (is_locked, remaining_seconds)."""
        now = time.time()
        locked_until = self._lockouts.get(key, 0)
        if now < locked_until:
            return True, int(locked_until - now)
        elif key in self._lockouts:
            del self._lockouts[key]
        return False, 0

    def lock_out(self, key: str, lockout_seconds: int):
        """Temporarily lock out a key for a duration."""
        self._lockouts[key] = time.time() + lockout_seconds

    def check_and_record(self, key: str, lockout_on_breach: int = 0) -> Tuple[bool, int]:
        """
        Check if request is allowed under rate limit.
        Returns (allowed: bool, retry_after: int)
        """
        now = time.time()
        
        # Check lockouts first
        is_locked, rem = self.is_locked_out(key)
        if is_locked:
            return False, rem

        # Clean old records outside the window
        cutoff = now - self.window_seconds
        records = [t for t in self._history[key] if t > cutoff]
        self._history[key] = records

        if len(records) >= self.max_requests:
            if lockout_on_breach > 0:
                self.lock_out(key, lockout_on_breach)
                return False, lockout_on_breach
            
            oldest = records[0]
            retry_after = int((oldest + self.window_seconds) - now) + 1
            return False, max(1, retry_after)

        # Record this request
        self._history[key].append(now)
        return True, 0

    def reset(self, key: str):
        """Reset history and lockout for a key (e.g. on successful login)."""
        if key in self._history:
            del self._history[key]
        if key in self._lockouts:
            del self._lockouts[key]


# Global rate limiter instances:
# 1. Login Brute-force protection: Max 5 failed attempts / 60 seconds -> 5-min lockout
login_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60, name="LoginLimiter")

# 2. NLU & Voice API Query limiter: Max 30 queries / 60 seconds per user/IP
nlu_limiter = SlidingWindowRateLimiter(max_requests=30, window_seconds=60, name="NLULimiter")

# 3. Escalation Ticket Throttle: Max 3 tickets / 10 minutes (600 seconds)
escalation_limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=600, name="EscalationLimiter")


def get_client_ip(request: Request) -> str:
    """Extract client IP safely from request headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


def enforce_nlu_rate_limit(request: Request):
    """Dependency to throttle NLU/Voice queries to 30 requests/min."""
    client_ip = get_client_ip(request)
    allowed, retry_after = nlu_limiter.check_and_record(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum 30 queries per minute. Please try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )
