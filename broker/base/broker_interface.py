"""
========================================================================

RUSI Trader AI

Broker Interface

========================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from broker.base.broker_order import BrokerOrder
from broker.base.broker_response import BrokerResponse


class BrokerInterface(ABC):

    @abstractmethod
    def place_order(
        self,
        order: BrokerOrder,
    ) -> BrokerResponse:
        raise NotImplementedError

    @abstractmethod
    def cancel_order(
        self,
        order_id: str,
    ) -> BrokerResponse:
        raise NotImplementedError

    @abstractmethod
    def get_order_status(
        self,
        order_id: str,
    ) -> BrokerResponse:
        raise NotImplementedError
