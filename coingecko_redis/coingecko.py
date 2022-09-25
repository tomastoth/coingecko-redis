import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from pycoingecko import CoinGeckoAPI
from pydantic import BaseModel

from coingecko_redis.async_utils import wrap_async
from coingecko_redis.config import config
from coingecko_redis.redis_client import PriceCache

logger = logging.getLogger(__name__)


class MarketUpdate(BaseModel):
    symbol: str
    current_price: Optional[float]


class PriceProvider(ABC):
    """
    Provides interface for price provision
    """

    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[float]:
        pass


class CoingeckoClient(PriceProvider):
    """
    Provides querying of crypto prices, which we then save to the cache
    """

    PRICES_PER_PAGE = 250

    def __init__(self, price_cache: PriceCache):
        """
        Creates CoinGeckoClient with default pycoigecko client
        """
        self._coingecko = CoinGeckoAPI()
        self._price_cache = price_cache

    async def price_update_loop(self):
        page = 1
        prices = {}
        while True:
            markets_data = await self._request_market_data(page)
            if not markets_data:
                continue
            for single_update in markets_data:
                self._add_market_update(prices, MarketUpdate.parse_obj(single_update))
            if len(markets_data) == self.PRICES_PER_PAGE and page <= 10:
                page += 1
            else:
                page = 1
                await self._update_prices_in_cache(prices)

    async def get_price(self, symbol: str) -> Optional[float]:
        found_price = await self._request_price(symbol)
        if found_price:
            return found_price[symbol]["usd"]
        return None

    @wrap_async
    def _request_price(self, symbol: str):
        """Requests the rpice using coingecko client, gets wrapped so we can use it async

        Args:
            symbol (str): symbol of the cryptocurrency to get price for

        Returns:
            string: coingecko response
        """
        return self._coingecko.get_price(symbol, vs_currencies=["usd"])

    @wrap_async
    def _request_market_data(self, page: int) -> Any:
        return self._coingecko.get_coins_markets("usd", per_page=self.PRICES_PER_PAGE, page=page)

    def _add_market_update(self, prices, market_update):
        if market_update.current_price:
            prices[market_update.symbol] = market_update.current_price

    async def _update_prices_in_cache(self, prices):
        await self._price_cache.update_prices(prices)
        logger.info("updating", prices)
        logger.info("Sleeping for 60 sec")
        await asyncio.sleep(config.price_save_interval_sec)
