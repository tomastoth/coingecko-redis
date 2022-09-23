from abc import ABC, abstractmethod
from typing import Optional

from pycoingecko import CoinGeckoAPI

from coingecko_redis.async_utils import wrap_async


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

    def __init__(self):
        """
        Creates CoinGeckoClient with default pycoigecko client
        """
        self._coingecko = CoinGeckoAPI()

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
