from abc import ABC, abstractmethod
from typing import Dict, Optional

import redis.asyncio as redis

from coingecko_redis.config import config


class PriceCache(ABC):
    """
    Interface for price caching
    """

    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[float]:
        """
        Interface that enables getting of price from cache

        Args:
            symbol (str): symbol of crypto to get price for

        Returns:
            Optional[float]: float if price is in cache None otherwise
        """
        pass

    @abstractmethod
    async def update_prices(self, new_prices: Dict[str, float]):
        """
        Enables updating of price in cache

        Args:
            new_prices (Dict[str,float]): dict of new prices
        """
        pass


class RedisClient(PriceCache):
    """
    Redis price cache client, enables getting the price from cache and updating it
    """

    def __init__(self):
        """
        Creates redis client using the python Redis implementation
        """
        self._redis = redis.Redis(host=config.redis_host, port=config.redis_port, db=config.redis_db)

    async def get_price(self, symbol: str) -> Optional[float]:
        found_price = await self._redis.get(symbol)
        if found_price:
            return float(found_price)
        return None

    async def update_prices(self, new_prices: Dict[str, float]):
        return await self._redis.mset(new_prices)
