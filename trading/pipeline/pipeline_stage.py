from abc import ABC, abstractmethod

from trading.context.trading_context import TradingContext


class PipelineStage(ABC):

    @property
    @abstractmethod
    def stage_name(self) -> str:
        """
        Human readable stage name.
        """
        raise NotImplementedError

    def before_execute(
        self,
        context: TradingContext,
    ) -> None:
        """
        Optional hook.
        """
        pass

    @abstractmethod
    def execute(
        self,
        context: TradingContext,
    ) -> TradingContext:
        raise NotImplementedError

    def after_execute(
        self,
        context: TradingContext,
    ) -> None:
        """
        Optional hook.
        """
        pass
