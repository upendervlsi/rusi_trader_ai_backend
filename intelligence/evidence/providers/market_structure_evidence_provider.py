"""
============================================================

Market Structure Evidence Provider

============================================================
"""

from intelligence.adapters.engine_to_evidence_adapter import (
    EngineToEvidenceAdapter,
)

from intelligence.evidence.evidence_provider import (
    EvidenceProvider,
)


class MarketStructureEvidenceProvider(
    EvidenceProvider
):

    def __init__(
        self,
        structure_engine,
    ):

        self._structure_engine = structure_engine

        self._adapter = (
            EngineToEvidenceAdapter()
        )

    @property
    def name(self):

        return "MarketStructure"

    def evaluate(
        self,
        context,
    ):

        result = self._structure_engine.run(
            context.snapshot
        )

        return self._adapter.convert(

            provider_name="MarketStructure",

            result=result,

            weight=1.4,
        )
