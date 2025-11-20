from unittest import mock

import pytest
from vcr_utils import vcr_utils

from tradingview_client import TradingViewClient
from tradingview_client.tradingview_client_exceptions import SymbolAtExchangeUnknown


class TestTradingViewClientReadLatestPrice:
    def setup_method(self):
        self.client = TradingViewClient()

    @vcr_utils(
        "tradingview_client.tradingview_client.TradingViewClient._read_latest_price_raw"
    )
    def test_happy_flow(self):
        response = self.client.read_latest_price(
            "TSLA", exchange="NASDAQ", do_use_extended_trading_hours=True
        )
        assert response.date.isoformat() == "2025-08-09T01:59:00"
        assert response.symbol == "TSLA"
        assert response.exchange == "NASDAQ"
        assert response.open_price == 330.0
        assert response.close_price == 329.99
        assert response.high_price == 330.0
        assert response.low_price == 329.98
        assert response.volume == 257.0

    # This tests prove that the close price for 1 hour interval is the latest price.
    # It proves it by comparing it with the 1 min interval.
    # However, @vcr_utils has the limitation that it only records one stub per test
    #  and this tests invokes twice the stubbed method, so it's commented out.
    # def test_interval_1_hour(self):
    #     response1h = self.client.read_latest_price(
    #         "ETHUSD",
    #         exchange="KRAKEN",
    #         interval=Interval.in_1_hour,
    #         do_use_extended_trading_hours=True,
    #     )
    #
    #     response1m = self.client.read_latest_price(
    #         "ETHUSD",
    #         exchange="KRAKEN",
    #         do_use_extended_trading_hours=True,
    #     )
    #
    #     assert response1h.close_price == response1m.close_price
    #     assert response1h.high_price != response1m.high_price

    @vcr_utils(
        "tradingview_client.tradingview_client.TradingViewClient._read_latest_price_raw"
    )
    def test_all_security_types(self):
        symbols = (
            ("TSLA", "NASDAQ", False),
            ("LDO", "MIL", False),
            ("VOO", "AMEX", False),
            ("ES", "CME_MINI", True),
            ("ETHUSD", "KRAKEN", False),
            ("ORAIUSDT", "KUCOIN", False),
        )
        for symbol, exchange, is_future_contract in symbols:
            response = self.client.read_latest_price(
                symbol,
                exchange=exchange,
                is_future_contract=is_future_contract,
                do_use_extended_trading_hours=True,
            )
            assert response.date.isoformat()
            assert response.symbol
            assert response.close_price

    @vcr_utils(
        "tradingview_client.tradingview_client.TradingViewClient._read_latest_price_raw"
    )
    def test_symbol_unknown(self):
        with pytest.raises(SymbolAtExchangeUnknown):
            self.client.read_latest_price(
                "ETHUSD", exchange="NASDAQ", do_use_extended_trading_hours=True
            )

    @vcr_utils(
        "tradingview_client.tradingview_client.TradingViewClient._read_latest_price_raw"
    )
    def test_exchange_unknown(self):
        with pytest.raises(SymbolAtExchangeUnknown):
            self.client.read_latest_price(
                "TSLA", exchange="KRAKEN", do_use_extended_trading_hours=True
            )

    @vcr_utils(
        "tradingview_client.tradingview_client.TradingViewClient._read_latest_price_raw"
    )
    def test_dataframe(self):
        response = self.client.read_latest_price(
            "TSLA", exchange="NASDAQ", do_use_extended_trading_hours=True
        )
        assert response.raw_dataframe.iloc[-1].open == 330.0
        assert response.raw_dataframe.iloc[-1].high == 330.0
        assert response.raw_dataframe.iloc[-1].low == 329.98
        assert response.raw_dataframe.iloc[-1].close == 329.99
        assert response.raw_dataframe.iloc[-1].volume == 257.0
        assert (
            response.raw_dataframe.index[-1].to_pydatetime().isoformat()
            == "2025-08-09T01:59:00"
        )

    def test_no_retries(self):
        with (
            pytest.raises(SymbolAtExchangeUnknown),
            mock.patch(
                "tradingview_client.tradingview_client.TradingViewClient._read_latest_price_raw",
                wraps=TradingViewClient._read_latest_price_raw,
                return_value=None,
                n_retries_if_response_is_none=0,
            ) as mocked_method,
        ):
            self.client.read_latest_price(
                "TSLA",
                exchange="NASDAQ",
            )
        assert mocked_method.call_count == 1

    def test_5_retries(self):
        with (
            pytest.raises(SymbolAtExchangeUnknown),
            mock.patch(
                "tradingview_client.tradingview_client.TradingViewClient._read_latest_price_raw",
                wraps=TradingViewClient._read_latest_price_raw,
                return_value=None,
            ) as mocked_method,
        ):
            self.client.read_latest_price(
                "TSLA",
                exchange="NASDAQ",
                n_retries_if_response_is_none=5,
            )
        assert mocked_method.call_count == 6
        assert True
