"""
============================================================
RUSI Trader AI

V1.0

Order Models Unit Tests
============================================================
"""

from tools.execution.order_models import (
    OrderRequest,
    OrderResult,
    OrderSide,
    OrderStatus,
    OrderType,
    TimeInForce,
)


class TestOrderModels:

    # ---------------------------------------------------------

    def test_order_side_enum(self):

        assert OrderSide.BUY.value == "BUY"
        assert OrderSide.SELL.value == "SELL"

    # ---------------------------------------------------------

    def test_order_type_enum(self):

        assert OrderType.MARKET.value == "MARKET"
        assert OrderType.LIMIT.value == "LIMIT"

    # ---------------------------------------------------------

    def test_order_request(self):

        request = OrderRequest(
            symbol="INFY",
            side=OrderSide.BUY,
            quantity=10,
            order_type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY,
        )

        assert request.symbol == "INFY"
        assert request.side == OrderSide.BUY
        assert request.quantity == 10
        assert request.order_type == OrderType.MARKET
        assert request.time_in_force == TimeInForce.DAY

    # ---------------------------------------------------------

    def test_order_result(self):

        result = OrderResult(
            order_id="ORD001",
            symbol="INFY",
            side=OrderSide.BUY,
            quantity=10,
        )

        assert result.order_id == "ORD001"
        assert result.status == OrderStatus.NEW

    # ---------------------------------------------------------

    def test_is_open(self):

        result = OrderResult(
            order_id="ORD001",
            symbol="INFY",
            side=OrderSide.BUY,
            quantity=10,
        )

        assert result.is_open
        assert not result.is_completed

    # ---------------------------------------------------------

    def test_is_completed(self):

        result = OrderResult(
            order_id="ORD001",
            symbol="INFY",
            side=OrderSide.BUY,
            quantity=10,
            status=OrderStatus.FILLED,
        )

        assert result.is_completed
        assert not result.is_open

    # ---------------------------------------------------------

    def test_timestamp(self):

        result = OrderResult(
            order_id="ORD001",
            symbol="INFY",
            side=OrderSide.BUY,
            quantity=10,
        )

        assert result.timestamp is not None

    # ---------------------------------------------------------

    def test_string(self):

        result = OrderResult(
            order_id="ORD001",
            symbol="INFY",
            side=OrderSide.BUY,
            quantity=10,
        )

        assert "OrderResult" in str(result)
        assert "OrderResult" in repr(result)
