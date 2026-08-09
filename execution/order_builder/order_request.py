from dataclasses import dataclass


@dataclass(slots=True)
class OrderRequest:

    symbol: str

    exchange: str

    transaction_type: str

    quantity: int
    #
    # Expected execution price.
    # For paper trading this is the simulated fill price.
    # For live trading this represents the requested order price
    # (or the estimated market price for MARKET orders).
    #
    execution_price: float

    order_type: str

    product_type: str
