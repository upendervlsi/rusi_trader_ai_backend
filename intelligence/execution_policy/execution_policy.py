from abc import ABC, abstractmethod

from intelligence.decision.decision import Decision
from intelligence.execution_policy.execution_policy_result import (
    ExecutionPolicyResult,
)


class ExecutionPolicy(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def evaluate(
        self,
        decision: Decision,
    ) -> ExecutionPolicyResult:
        ...
