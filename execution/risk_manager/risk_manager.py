from abc import ABC, abstractmethod

from execution.order_builder.order_request import OrderRequest
from execution.risk_manager.risk_result import RiskResult


class RiskManager(ABC):

    @abstractmethod
    def evaluate(
        self,
        order: OrderRequest,
    ) -> RiskResult:
        ...
