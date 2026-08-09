from abc import ABC, abstractmethod

from intelligence.models.feature_store import FeatureStore
from intelligence.signals.signal_result import SignalResult


class BaseRule(ABC):

    @abstractmethod
    def evaluate(
        self,
        feature_store: FeatureStore,
    ) -> SignalResult:
        """
        Evaluate the trading rule and return a SignalResult.
        """
        raise NotImplementedError
