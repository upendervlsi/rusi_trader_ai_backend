"""
============================================================
RUSI Trader AI

V1.0

Trading Pipeline
============================================================
"""

from __future__ import annotations

from tools.pipeline.pipeline_models import (
    PipelineResult,
    TradingContext,
    TradingRequest,
)


class TradingPipeline:
    """
    End-to-end trading pipeline.

    Coordinates all major engines in sequence.
    """

    def __init__(
        self,
        scanner_engine=None,
        indicator_engine=None,
        decision_engine=None,
        confidence_engine=None,
        risk_engine=None,
        portfolio_engine=None,
        execution_engine=None,
    ):

        self.scanner_engine = scanner_engine
        self.indicator_engine = indicator_engine
        self.decision_engine = decision_engine
        self.confidence_engine = confidence_engine
        self.risk_engine = risk_engine
        self.portfolio_engine = portfolio_engine
        self.execution_engine = execution_engine

    # -----------------------------------------------------

    def execute(
        self,
        request: TradingRequest,
    ) -> PipelineResult:
        """
        Execute the complete trading pipeline.
        """

        context = TradingContext(request=request)

        if self.scanner_engine is not None:
            context.scanner_result = (
                self.scanner_engine.scan(request)
            )

        if self.indicator_engine is not None:
            context.indicator_result = (
                self.indicator_engine.compute(
                    context.scanner_result
                )
            )

        if self.decision_engine is not None:
            context.decision_result = (
                self.decision_engine.evaluate(
                    context.indicator_result
                )
            )

        if self.confidence_engine is not None:
            context.confidence_result = (
                self.confidence_engine.calculate(
                    context.decision_result
                )
            )

        if self.risk_engine is not None:
            context.risk_result = (
                self.risk_engine.evaluate(
                    context.decision_result,
                    context.confidence_result,
                )
            )

        if self.portfolio_engine is not None:
            context.portfolio_result = (
                self.portfolio_engine.process(
                    context.risk_result
                )
            )

        if self.execution_engine is not None:
            context.execution_result = (
                self.execution_engine.process(
                    context.portfolio_result
                )
            )

        return PipelineResult(
            success=True,
            context=context,
            message="Pipeline completed successfully.",
        )

    # -----------------------------------------------------

    def __str__(self):

        return (
            "TradingPipeline("
            "scanner="
            f"{self.scanner_engine is not None}, "
            "indicator="
            f"{self.indicator_engine is not None}, "
            "decision="
            f"{self.decision_engine is not None})"
        )

    __repr__ = __str__
