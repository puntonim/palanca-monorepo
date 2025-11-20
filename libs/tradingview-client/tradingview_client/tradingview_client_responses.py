import importlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .tradingview_client_exceptions import MissingOptionalDependency

__all__ = ["ReadLatestPriceResponse"]


class BaseTradingviewClientResponse:
    def __init__(self, raw_data: Any):
        self.raw_data = raw_data

    def to_dict(self) -> dict:
        return self.raw_data.to_dict()


@dataclass
class Ohlc:
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str
    exchange: str


class ReadLatestPriceResponse(BaseTradingviewClientResponse):
    def __init__(self, raw_data: list, symbol: str, exchange: str):
        super().__init__(raw_data)

        self.data = list()
        for d in raw_data:
            self.data.append(
                Ohlc(
                    ts=d[0],
                    open=d[1],
                    high=d[2],
                    low=d[3],
                    close=d[4],
                    volume=d[5],
                    symbol=symbol,
                    exchange=exchange,
                )
            )

    @property
    def ohlc(self) -> Ohlc:
        return self.data[0]

    @property
    def open_price(self) -> float:
        return self.ohlc.open

    @property
    def close_price(self) -> float:
        return self.ohlc.close

    @property
    def high_price(self) -> float:
        return self.ohlc.high

    @property
    def low_price(self) -> float:
        return self.ohlc.low

    @property
    def volume(self) -> float:
        return self.ohlc.volume

    @property
    def symbol(self) -> str:
        return self.ohlc.symbol

    @property
    def exchange(self) -> str:
        return self.ohlc.exchange

    @property
    def date(self) -> datetime:
        return self.ohlc.ts

    @property
    def raw_dataframe(self) -> "pd.DataFrame":  # noqa: F821
        # Dynamic import, since pandas is an optional extra.
        # Mind that pandas has some troubles with AWS Lambda, see README.md.
        try:
            pd = importlib.import_module("pandas")
        except ModuleNotFoundError as exc:
            raise MissingOptionalDependency("pandas") from exc

        df = pd.DataFrame(
            self.raw_data,
            columns=["datetime", "open", "high", "low", "close", "volume"],
        ).set_index("datetime")
        df.insert(0, "symbol", value=self.symbol)
        df.insert(0, "exchange", value=self.exchange)

        return df
