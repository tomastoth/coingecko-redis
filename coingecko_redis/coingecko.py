import asyncio
import logging
from typing import Any, Optional, Dict

from pycoingecko import CoinGeckoAPI
from pydantic import BaseModel

from coingecko_redis.async_utils import wrap_async
from coingecko_redis.config import config
from coingecko_redis.redis_client import PriceCacheWriter

logger = logging.getLogger(__name__)


class MarketUpdate(BaseModel):
    symbol: str
    current_price: Optional[float]


class CoingeckoClient:
    """
    Provides querying of crypto prices, which we then save to the cache
    """

    PRICES_PER_PAGE = 250

    def __init__(self, price_cache: PriceCacheWriter):
        """
        Creates CoinGeckoClient with default pycoigecko client
        """
        self._coingecko = CoinGeckoAPI()
        self._price_cache = price_cache

    async def price_update_loop(self) -> None:
        """
        Loops indefinitely, querying coingecko prices and saving them to cache
        """
        page = 1
        prices = {}
        while True:
            try:
                page = await self._price_fetch_save_iteration(page, prices)
            except Exception as e:
                logger.error("Exception while price fetch save iteration")
                logger.error(e)
                continue
            if page == 1:
                logger.info(f"Sleeping for {config.price_save_interval_sec} sec")
                await asyncio.sleep(config.price_save_interval_sec)

    @staticmethod
    def _add_market_update(prices, market_update):
        if market_update.current_price:
            prices[market_update.symbol] = market_update.current_price

    async def _price_fetch_save_iteration(self, page: int, prices: Dict[str, float]) -> int:
        """
        Queries price data from coingecko and saves them to cache
        :param page: page of coingecko price updates
        :param prices: dict where to save
        :return:  returns page that is left to query, 1 if we are done (so we can continue loop)
        """
        markets_data = await self._request_market_data(page)
        if not markets_data:
            logger.warning("We got no market data from coingecko")
            return 1
        for single_update in markets_data:
            self._add_market_update(prices, MarketUpdate.parse_obj(single_update))
        if len(markets_data) == self.PRICES_PER_PAGE and page <= 10:
            page += 1
        else:
            page = 1
            await self._update_prices_in_cache(prices)
        return page

    @wrap_async
    def _request_price(self, symbol: str):
        """Requests the price using coingecko client, gets wrapped so we can use it async

        Args:
            symbol (str): symbol of the cryptocurrency to get price for

        Returns:
            string: coingecko response
        """
        return self._coingecko.get_price(symbol, vs_currencies=["usd"])

    @wrap_async
    def _request_market_data(self, page: int) -> Any:
        return self._coingecko.get_coins_markets("usd", per_page=self.PRICES_PER_PAGE, page=page)

    async def _update_prices_in_cache(self, prices):
        try:
            await self._price_cache.update_prices(prices)
            logger.info("updating prices")
        except Exception as e:
            logger.error("Could not update prices in cache!")
            logger.error(e)
