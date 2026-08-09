from abc import ABC, abstractmethod

from intelligence.decision.decision import Decision
from execution.order_builder.order_request import OrderRequest


class OrderBuilder(ABC):

    @abstractmethod
    def build(
        self,
        decision: Decision,
    ) -> OrderRequest:
        ...
