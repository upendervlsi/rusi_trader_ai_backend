"""
========================================================================

RUSI Trader AI

Angel One Broker

========================================================================
"""

from __future__ import annotations

from broker.angel_one.angel_one_client import (
    AngelOneClient,
)
from broker.angel_one.order_mapper import (
    AngelOrderMapper,
)
from broker.base.broker_interface import (
    BrokerInterface,
)
from broker.base.broker_order import (
    BrokerOrder,
)
from broker.base.broker_response import (
    BrokerResponse,
)


class AngelOneBroker(BrokerInterface):

    def __init__(
        self,
        client: AngelOneClient,
    ) -> None:

        self._client = client

        self._mapper = AngelOrderMapper()

    def place_order(
        self,
        order: BrokerOrder,
    ) -> BrokerResponse:

        raise NotImplementedError(
            "Will be implemented in Sprint-73."
        )

    def cancel_order(
        self,
        order_id: str,
    ) -> BrokerResponse:

        raise NotImplementedError

    def get_order_status(
        self,
        order_id: str,
    ) -> BrokerResponse:

        raise NotImplementedError
