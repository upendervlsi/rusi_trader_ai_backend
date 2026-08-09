from common.signal_type import SignalType
from intelligence.execution_policy.execution_policy import (
    ExecutionPolicy,
)
from intelligence.execution_policy.execution_policy_result import (
    ExecutionPolicyResult,
)


class DefaultExecutionPolicy(
    ExecutionPolicy
):

    @property
    def name(self) -> str:
        return "DefaultExecutionPolicy"

    def evaluate(
        self,
        decision,
    ) -> ExecutionPolicyResult:

        #
        # HOLD decisions are never executed
        #

        if decision.signal == SignalType.HOLD:

            return ExecutionPolicyResult(
                trade_allowed=False,
                reason="Decision is HOLD",
            )

        #
        # Confidence filter
        #

        if decision.confidence < 60:

            return ExecutionPolicyResult(
                trade_allowed=False,
                reason="Confidence below threshold",
            )

        return ExecutionPolicyResult(
            trade_allowed=True,
            reason="Execution approved",
        )
