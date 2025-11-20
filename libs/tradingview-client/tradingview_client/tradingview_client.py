"""
** TRADINGVIEW CLIENT **
========================

TradingView client to get live and historical prices f securities.
This client uses un-official TradingView API and it is based on the lib TvDatafeed,
 which I copied and improved in this repo.
TvDatafeed src: https://github.com/rongardF/tvdatafeed/blob/main/tvDatafeed/main.py

This client has many issues due to the fact that it's based on un-official API, not
 really meant for this usage.
It works well for historical data, not to well for live data.

Pros:
 - TradingView has data on many securities and cryptos at many exchanges.
 - Data is free.

Cons:
 - unclear threshold around 3 req/sec, after which I get the status 429 Too Many Requests.
 - sometimes (often) requests fail returning None (which is also the response for
    unknown symbols), so I had to implement a retry strategy.
"""

import retry_utils

from . import tradingview_client_exceptions as exceptions
from .tradingview_client_responses import ReadLatestPriceResponse
from .tvdatafeed import Interval, TvDatafeed

__all__ = [
    "TradingViewClient",
    "Interval",
]

# TODO all logging
# TODO support auth with my username and pass, ma ocio a vcr


class TradingViewClient:
    def __init__(self, username: str | None = None, password: str | None = None):
        self.tv = TvDatafeed(username=username, password=password)

    def read_latest_price(
        self,
        symbol: str,
        exchange: str,
        interval: Interval = Interval.in_1_minute,
        is_future_contract: bool = False,
        do_use_extended_trading_hours: bool = False,
        n_retries_if_response_is_none: int = 0,
    ) -> ReadLatestPriceResponse:
        """
        Read the latest price for the given symbol at the given exchange.
        It works for stocks, indices, futures, crypto.

        Args:
            symbol (str): eg. "TSLA". See docs/info simbolo *.png in https://github.com/puntonim/palanca-monorepo/tree/main/libs/tradingview-client/docs.
            exchange (str): eg. "NASDAQ". See docs/info simbolo *.png in https://github.com/puntonim/palanca-monorepo/tree/main/libs/tradingview-client/docs.
            interval (Interval): candle interval, eg. Interval.in_1_minute.
            is_future_contract: True for futures like ES at CME_MINI.
            do_use_extended_trading_hours: True to return the price during
             extended trading hours.
            n_retries_if_response_is_none: sometimes (often) the response is None even
             for a known symbol/exchange. In this case it safe to retry. But mind that
             the response is None also for unknown symbols, so do use this arg only
             when very sure about the given symbol/exchange.

        Example:
            client = TradingViewClient()
            response = client.read_latest_price(
                "TSLA", exchange="NASDAQ", do_use_extended_trading_hours=True
            )
            print(response.date, response.symbol, response.close_price)
        """
        if n_retries_if_response_is_none > 10:
            raise ValueError("max value for n_retries_if_response_is_none is 10")

        @retry_utils.retry_if_exc(
            n_retries_after_1st_failure=n_retries_if_response_is_none,
            sleep_sec=0.2,
            do_not_raise_exc_on_max_retries_reached=True,
        )
        def x():
            # Sometimes (often) the response is None even for a valid symbol/exchange.
            #  In this case it safe to retry. But mind that the response is None also
            #  for unknown symbols, so do use this arg only when very sure about the
            #  given symbol/exchange.
            d = self._read_latest_price_raw(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                is_future_contract=is_future_contract,
                do_use_extended_trading_hours=do_use_extended_trading_hours,
            )
            if d is None:
                raise retry_utils.RetryException
            return d

        data: list | None = x()

        if data is None:
            raise exceptions.SymbolAtExchangeUnknown(symbol, exchange)

        elif isinstance(data, list) and not data:
            raise exceptions.EmptyData

        return ReadLatestPriceResponse(data, symbol, exchange)

    def _read_latest_price_raw(
        self,
        symbol: str,
        exchange: str,
        interval: Interval = Interval.in_1_minute,
        is_future_contract: bool = False,
        do_use_extended_trading_hours: bool = False,
    ) -> list | None:
        # IMP: this private method is required for proper testing with @vcr_utils.
        #  It must execute ONLY the Websocket connection (via the lib tvDatafeed, that
        #  I copied in tvdatafeed.py)
        # There should be no code here apart from just making the Websocket request.

        # Note: sometimes (often) the response is None even for a valid symbol/exchange.

        data: list | None = self.tv.get_hist(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            n_bars=1,
            fut_contract=1 if is_future_contract else None,
            extended_session=do_use_extended_trading_hours,
        )
        return data
