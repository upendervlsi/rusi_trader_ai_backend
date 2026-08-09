"""
============================================================

Trade Record

============================================================
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class TradeRecord:

    trade_id: str

    order_id: str

    position_id: str

    symbol: str

    exchange: str

    transaction_type: str

    quantity: int

    entry_price: float

    decision_signal: str

    decision_score: float

    decision_confidence: float

    execution_time: datetime

    status: str
