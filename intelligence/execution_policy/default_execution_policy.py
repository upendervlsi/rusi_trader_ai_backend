from common.signal_type import SignalType

from config.trading_config import TradingConfig

from intelligence.execution_policy.execution_policy import (
    ExecutionPolicy,
)

from intelligence.execution_policy.execution_policy_result import (
    ExecutionPolicyResult,
)


class DefaultExecutionPolicy(
    ExecutionPolicy
):

    def __init__(
        self,
        config: TradingConfig | None = None,
    ) -> None:

        #
        # Central trading configuration.
        #
        # Execution thresholds must come from one
        # authoritative configuration instead of being
        # hard-coded inside the policy.
        #

        self._config = (
            config
            if config is not None
            else TradingConfig()
        )

    @property
    def name(self) -> str:

        return "DefaultExecutionPolicy"

    def evaluate(
        self,
        decision,
    ) -> ExecutionPolicyResult:

        #
        # -----------------------------------------------------
        # Decision validation
        # -----------------------------------------------------
        #

        if decision is None:

            return ExecutionPolicyResult(
                trade_allowed=False,
                reason="No decision available",
            )

        #
        # -----------------------------------------------------
        # HOLD decisions are never executed
        # -----------------------------------------------------
        #

        if decision.signal == SignalType.HOLD:

            return ExecutionPolicyResult(
                trade_allowed=False,
                reason="Decision is HOLD",
            )

        #
        # -----------------------------------------------------
        # Central confidence threshold
        # -----------------------------------------------------
        #
        # IMPORTANT:
        #
        # Do not hard-code the execution threshold here.
        #
        # TradingConfig.minimum_confidence is the single
        # source of truth.
        #

        minimum_confidence = (
            self._config.minimum_confidence
        )

        if (
            decision.confidence
            < minimum_confidence
        ):

            return ExecutionPolicyResult(
                trade_allowed=False,
                reason=(
                    "Confidence below threshold "
                    f"({decision.confidence:.2f} < "
                    f"{minimum_confidence:.2f})"
                ),
            )

        #
        # -----------------------------------------------------
        # Execution approved
        # -----------------------------------------------------
        #

        return ExecutionPolicyResult(
            trade_allowed=True,
            reason=(
                "Execution approved "
                f"(confidence {decision.confidence:.2f} >= "
                f"{minimum_confidence:.2f})"
            ),
        )
