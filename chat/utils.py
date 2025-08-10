import time
from django.core.cache import cache
from functools import wraps

def rate_limit(key_prefix: str, limit_seconds: int):
    """
    Decorator to rate limit a method per user.

    Usage:
      @rate_limit("typing_event", 2)
      async def handle_typing(self, ...):
          ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            user_id = getattr(self.user, "id", None)
            if not user_id:
                return await func(self, *args, **kwargs)

            cache_key = f"{key_prefix}:{user_id}"
            last_time = cache.get(cache_key)
            now = time.time()

            if last_time and now - last_time < limit_seconds:
                return

            cache.set(cache_key, now, timeout=limit_seconds)
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator
