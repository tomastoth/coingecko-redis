import asyncio
import logging

from coingecko_redis.coingecko import CoingeckoClient
from coingecko_redis.redis_client import RedisClient


async def run():
    """
    App entry point
    """
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting the application")
    redis = RedisClient()
    coin_gecko = CoingeckoClient(price_cache=redis)
    await coin_gecko.price_update_loop()


if __name__ == "__main__":
    asyncio.run(run())
