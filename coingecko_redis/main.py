import asyncio
import logging

from coingecko_redis.coingecko import CoingeckoClient
from coingecko_redis.redis_client import RedisClient


async def run():
    """
    App entry point
    """
    logging.info("Starting the application")
    redis = RedisClient()
    coin_gecko = CoingeckoClient()
    await redis.update_price("BTC", await coin_gecko.get_price("bitcoin"))
    logging.info(await redis.get_price("BTC"))
    logging.info("done")


if __name__ == "__main__":
    asyncio.run(run())
