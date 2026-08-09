"""
============================================================

Portfolio Model

============================================================
"""

from pydantic import BaseModel


class PortfolioModel(BaseModel):

    open_positions: int

    invested_amount: float

    market_value: float

    unrealized_pnl: float

    updated_time: str
