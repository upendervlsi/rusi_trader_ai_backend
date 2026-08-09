from intelligence.decision.decision import Decision
from intelligence.execution_policy.execution_policy import (
    ExecutionPolicy,
)


class ExecutionPolicyManager:

    def __init__(
        self,
        policy: ExecutionPolicy,
    ) -> None:

        self._policy = policy

    def evaluate(
        self,
        decision: Decision,
    ):

        return self._policy.evaluate(
            decision
        )
