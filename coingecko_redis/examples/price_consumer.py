import asyncio
import logging

from coingecko_redis.redis_client import PriceCacheReader

logger = logging.getLogger(__name__)


class RedisConsumer:
    """
    Connects to Redis server to read prices of ETH periodically
    """

    def __init__(self, price_cache: PriceCacheReader):
        self._price_cache: PriceCacheReader = price_cache

    async def keep_querying_eth_price(self):
        while True:
            eth_price = await self._price_cache.get_price("eth")
            logger.info(eth_price)
            await asyncio.sleep(2)
