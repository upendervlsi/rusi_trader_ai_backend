"""
============================================================
RUSI Trader AI

Unit Tests

Risk Models
============================================================
"""

from tools.risk.risk_models import (
    RiskDecision,
    RiskResult,
)


class TestRiskModels:

    def test_risk_decision_enum(self):

        assert RiskDecision.ALLOW.value == "ALLOW"
        assert RiskDecision.REDUCE_POSITION.value == "REDUCE_POSITION"
        assert RiskDecision.REJECT.value == "REJECT"

    # ---------------------------------------------------------

    def test_risk_result(self):

        result = RiskResult(
            decision=RiskDecision.ALLOW,
        )

        assert result.decision == RiskDecision.ALLOW
        assert result.position_size == 0.0
        assert result.stop_loss == 0.0
        assert result.target_price == 0.0
        assert result.risk_percent == 0.0
        assert result.reward_percent == 0.0
        assert result.risk_reward_ratio == 0.0
        assert result.maximum_loss == 0.0

    # ---------------------------------------------------------

    def test_add_reason(self):

        result = RiskResult(
            decision=RiskDecision.ALLOW,
        )

        result.add_reason(
            "Risk within limits"
        )

        assert len(result.reasons) == 1
        assert result.reasons[0] == "Risk within limits"

    # ---------------------------------------------------------

    def test_add_metadata(self):

        result = RiskResult(
            decision=RiskDecision.ALLOW,
        )

        result.add_metadata(
            "capital",
            100000,
        )

        assert result.metadata["capital"] == 100000

    # ---------------------------------------------------------

    def test_timestamp(self):

        result = RiskResult(
            decision=RiskDecision.ALLOW,
        )

        assert result.timestamp is not None

    # ---------------------------------------------------------

    def test_string(self):

        result = RiskResult(
            decision=RiskDecision.ALLOW,
            position_size=100,
            risk_reward_ratio=2.5,
        )

        assert "RiskResult" in str(result)
        assert "RiskResult" in repr(result)
