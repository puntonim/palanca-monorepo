"""
The goal of these tests is to find the rate-limit threshold for the un-official
 TradingView API.

Results:
 - 5 concurrent threads seems to NEVER hit the rate-limit, on my laptop. Even with
    a total of 31 requests.
 - 6 concurrent threads seems to ALWAYS hit the rate-limit, on my laptop.
 - the authenticated client has the same rate-limit as the anonymous one.
"""

import concurrent.futures

import pytest

from tradingview_client import Interval, TradingViewClient

SECURITIES = (
    ("ETHUSD", "KRAKEN"),
    ("SHRAPUSDT", "KUCOIN"),
    ("RPLUSDT", "KUCOIN"),
    ("ORAIUSDT", "KUCOIN"),
    ("ZCXUSDT", "KUCOIN"),
    ("XCADUSDT", "KUCOIN"),
    ("FETUSDT", "KUCOIN"),
    ("WAXLUSDT", "KUCOIN"),
    ("ARTYUSDT", "KUCOIN"),
    ("VRAUSDT", "KUCOIN"),
    ("AVAXUSD", "KRAKEN"),
    ("ARBUSD", "KRAKEN"),
    ("BTCUSD", "KRAKEN"),
    ("BTCEUR", "KRAKEN"),
    ("BTCCHF", "KRAKEN"),
    ("ETHEUR", "KRAKEN"),
    ("ETHCHF", "KRAKEN"),
    ("ADAUSD", "KRAKEN"),
    ("ADABTC", "KRAKEN"),
    ("XRPUSD", "KRAKEN"),
    ("XRPBTC", "KRAKEN"),
    ("TSLA", "NASDAQ"),
    ("AAPL", "NASDAQ"),
    ("GOOGL", "NASDAQ"),
    ("NVDA", "NASDAQ"),
    ("AMZN", "NASDAQ"),
    ("KO", "NYSE"),
    ("F", "NYSE"),
    ("CVX", "NYSE"),
    ("TWLO", "NYSE"),
    ("TSM", "NYSE"),
)


def _worker(symbol: str, exchange: str, client: TradingViewClient | None = None):
    if client is None:
        client = TradingViewClient()
    resp = client.read_latest_price(
        symbol,
        exchange=exchange,
        interval=Interval.in_1_hour,
        do_use_extended_trading_hours=True,
        n_retries_if_response_is_none=5,
    )
    return f"{resp.symbol}: {resp.close_price}"


@pytest.mark.skip(reason="Only run them when needed")
class TestAnonymousClient:
    def test_5_threads(self):
        """
        31 securities with 5 concurrent threads and n_retries_if_response_is_none=5.

        Run 1:
            No errors.
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:16.87
        Run 2:
            No errors.
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:20.23
        Run 3:
            No errors.
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:18.15
        Run 4:
            No errors.
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:18.06
        Run 5:
            No errors.
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:19.80
        """
        client = TradingViewClient()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = list()
            for symbol, exchange in SECURITIES:
                futures.append(
                    executor.submit(
                        _worker, symbol=symbol, exchange=exchange, client=client
                    )
                )

            for future in concurrent.futures.as_completed(futures):
                if future.exception() is not None:
                    executor.shutdown(cancel_futures=True)
                    raise future.exception()
                print(future.result())

    def test_6_threads(self):
        """
        31 securities with 6 concurrent threads and n_retries_if_response_is_none=5.

        Run 1:
            429 Too Many Requests
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:04.25
        Run 2:
            429 Too Many Requests
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:03.77
        """
        client = TradingViewClient()
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = list()
            for symbol, exchange in SECURITIES:
                futures.append(
                    executor.submit(
                        _worker, symbol=symbol, exchange=exchange, client=client
                    )
                )

            for future in concurrent.futures.as_completed(futures):
                if future.exception() is not None:
                    executor.shutdown(cancel_futures=True)
                    raise future.exception()
                print(future.result())

    def test_7_threads(self):
        """
        31 securities with 7 concurrent threads and n_retries_if_response_is_none=5.

        Run 1:
            429 Too Many Requests
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:04.71
        Run 2:
            429 Too Many Requests
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:03.92
        """
        client = TradingViewClient()
        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
            futures = list()
            for symbol, exchange in SECURITIES:
                futures.append(
                    executor.submit(
                        _worker, symbol=symbol, exchange=exchange, client=client
                    )
                )

            for future in concurrent.futures.as_completed(futures):
                if future.exception() is not None:
                    executor.shutdown(cancel_futures=True)
                    raise future.exception()
                print(future.result())


@pytest.mark.skip(reason="Only run them when needed")
class TestAuthClient:
    """
    The goal of these tests is to see if the client with proper authentication has
     a higher rate-limit threshold than the anonymous client.
    The answer is NO: it has the same rate-limit threshold as the anonymous client.
    """

    def test_5_threads(self):
        """
        31 securities with 5 concurrent threads and n_retries_if_response_is_none=5.

        Run 1:
            No errors.
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:22.53
        Run 2:
            No errors.
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:19.00
        Run 3:
            No errors.
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:18.09
        Run 4:
            No errors.
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:13.31
        Run 5:
            No errors.
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:19.89
        """
        # TODO Use valid creds for the actual test.
        client = TradingViewClient(username="XXX", password="XXX")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = list()
            for symbol, exchange in SECURITIES:
                futures.append(
                    executor.submit(
                        _worker, symbol=symbol, exchange=exchange, client=client
                    )
                )

            for future in concurrent.futures.as_completed(futures):
                if future.exception() is not None:
                    executor.shutdown(cancel_futures=True)
                    raise future.exception()
                print(future.result())

    def test_7_threads(self):
        """
        31 securities with 7 concurrent threads and n_retries_if_response_is_none=5.

        Run 1:
            429 Too Many Requests
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:03.93
        Run 2:
            429 Too Many Requests
            Elapsed (wall clock) time (h:mm:ss or m:ss): 0:05.18
        """
        # TODO Use valid creds for the actual test.
        client = TradingViewClient(username="XXX", password="XXX")
        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
            futures = list()
            for symbol, exchange in SECURITIES:
                futures.append(
                    executor.submit(
                        _worker, symbol=symbol, exchange=exchange, client=client
                    )
                )

            for future in concurrent.futures.as_completed(futures):
                if future.exception() is not None:
                    executor.shutdown(cancel_futures=True)
                    raise future.exception()
                print(future.result())
