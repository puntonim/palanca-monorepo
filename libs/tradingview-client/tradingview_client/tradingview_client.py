"""
** TRADINGVIEW CLIENT **
========================

TradingView client to get live and historical prices of securities.

This client uses un-official TradingView API and it is based on the lib TvDatafeed,
 which I copied and edited in this repo. In particular, I removed the pandas
 dependency because it's not really necessary for my use cases and because it causes
 troubles in AWS Lambda (it requires a layer and quite some RAM allocated to the Lambda,
 and thus costly):
TvDatafeed src: https://github.com/rongardF/tvdatafeed/blob/main/tvDatafeed/main.py

This client has many reliability issues due to the fact that it's based on un-official
 API, not really meant for this usage.
However, I implemented a retry strategy and a multi-threading approach that seems to
 work within the rate-limit (I've never seen it failing).

Pros:
 - TradingView has data on many securities and cryptos at many exchanges.
 - Data is free.

Cons:
 - unknown threshold around 3 req/sec, after which I get the status 429 Too Many Requests.
   But I found that 5 concurrent threads seem to never hit the rate-limit.
 - sometimes (often) requests fail returning None (which is also the response for
    unknown symbols), so I implemented a retry strategy.
 - there is no API to request multiple symbols, so I implemented a multi-threading
    approach.
 - it's rate-limited, so I used the proper concurrency value for multi-threading,
    see next section.

Rate limits
-----------
 - 5 concurrent threads seems to NEVER hit the rate-limit, on my laptop. Even with
    a total of 31 requests.
 - 6 concurrent threads seems to ALWAYS hit the rate-limit, on my laptop.
 - the authenticated client has the same rate-limit as the anonymous one.

See tests/test_rate_limit_threshold.py.

So I used max_workers=5 in read_latest_prices_concurrently().
"""

import concurrent.futures
from collections.abc import Generator

import log_utils as logger
import retry_utils

from . import tradingview_client_exceptions as exceptions
from .tradingview_client_responses import ReadLatestPriceResponse
from .tvdatafeed import Interval, TvDatafeed

__all__ = [
    "TradingViewClient",
    "Interval",
]


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
            logger.info(f"Getting latest price for: {symbol} at {exchange}")
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
                logger.info(
                    f"Got None response for latest price for:  {symbol} at {exchange}, retrying..."
                )
                raise retry_utils.RetryException
            return d

        data: list | None = x()

        if data is None:
            raise exceptions.SymbolAtExchangeUnknown(symbol, exchange)

        elif isinstance(data, list) and not data:
            raise exceptions.EmptyData

        return ReadLatestPriceResponse(data, symbol, exchange)

    def read_latest_prices_concurrently(
        self, kwargs_to_read_latest_price: list[dict]
    ) -> Generator[ReadLatestPriceResponse]:
        """
        Read the latest prices for all the given symbols.
        It takes a list of kwargs, so list[dict], that is passed down to the method
         self.read_latest_price().

        It uses 5 concurrent threads. The optimal value of 5 was found with the tests in:
         tests/test_rate_limit_threshold.py.

        Args:
            kwargs_to_read_latest_price: list of kwargs passed down to the method
             self.read_latest_price().

        Returns: yields ReadLatestPriceResponse returned by self.read_latest_price().
        """
        # The optimal value max_workers=5 was found with the tests in
        #  tests/test_rate_limit_threshold.py.
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = list()
            for kwargs in kwargs_to_read_latest_price:
                futures.append(executor.submit(self.read_latest_price, **kwargs))

            for future in concurrent.futures.as_completed(futures):
                if future.exception() is not None:
                    # In case of exception in any thread, cancel the scheduled futures
                    #  and re-raise the exception.
                    executor.shutdown(cancel_futures=True)
                    raise future.exception()
                # Yield results as soon as they are available.
                yield future.result()

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
