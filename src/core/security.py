from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
import redis
from src.config import settings

# Redis client untuk rate limiting
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    strategy="moving-window"
)

# CORS config
def get_cors_origins():
    if settings.DEBUG:
        return ["*"]
    return ["https://yourdomain.com"]