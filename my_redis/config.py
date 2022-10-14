import redis.asyncio as redis


async def init_redis_pool() -> redis.Redis:
    redis_c = await redis.from_url(
        'redis://redis',
        encoding="utf-8",
        db=0,
        decode_responses=True,
    )
    return redis_c