from unittest.mock import patch, AsyncMock

import pytest

from coingecko_redis.coingecko import CoingeckoClient


@pytest.mark.asyncio
@patch("coingecko_redis.coingecko.CoingeckoClient._request_market_data")
async def test_saving_price(req_market_data):
    single_update = {"symbol": "eth", "current_price": 1500.0}
    req_market_data.return_value = [
        single_update
    ]
    price_writer_mock = AsyncMock()
    update_prices_mock: AsyncMock = price_writer_mock.update_prices
    cg = CoingeckoClient(price_writer_mock)
    await cg._price_fetch_save_iteration(1, {})
    expected_data = {"eth": 1500.0}
    update_prices_mock.assert_awaited_once_with(expected_data)
