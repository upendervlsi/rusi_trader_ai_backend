"""
============================================================

Trend Evidence Provider

============================================================
"""

from intelligence.adapters.engine_to_evidence_adapter import (
    EngineToEvidenceAdapter,
)

from intelligence.evidence.evidence_provider import (
    EvidenceProvider,
)


class TrendEvidenceProvider(
    EvidenceProvider
):

    def __init__(
        self,
        trend_engine,
    ):

        self._trend_engine = trend_engine

        self._adapter = (
            EngineToEvidenceAdapter()
        )

    @property
    def name(self):

        return "Trend"

    def evaluate(
        self,
        context,
    ):

        result = self._trend_engine.run(
            context.snapshot
        )

        return self._adapter.convert(

            provider_name="Trend",

            result=result,

            weight=1.2,
        )
