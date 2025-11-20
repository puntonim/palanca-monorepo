__all__ = [
    "BaseTradingViewClientException",
    "SymbolAtExchangeUnknown",
    "EmptyData",
    "MissingOptionalDependency",
]


class BaseTradingViewClientException(Exception):
    pass


class SymbolAtExchangeUnknown(BaseTradingViewClientException):
    def __init__(self, symbol: str, exchange: str):
        self.symbol = symbol
        self.exchange = exchange


class EmptyData(BaseTradingViewClientException):
    pass


class MissingOptionalDependency(BaseTradingViewClientException):
    pass
