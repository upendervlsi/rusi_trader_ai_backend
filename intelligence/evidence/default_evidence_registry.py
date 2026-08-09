"""
========================================================================

RUSI Trader AI

Default Evidence Registry

========================================================================
"""

from __future__ import annotations

from intelligence.evidence.evidence_manager import EvidenceManager
from intelligence.evidence.evidence_provider_registry import (
    EvidenceProviderRegistry,
)
from intelligence.evidence.providers.ema_evidence_provider import (
    EMAEvidenceProvider,
)
from intelligence.evidence.providers.rsi_evidence_provider import (
    RSIEvidenceProvider,
)
from intelligence.evidence.providers.macd_evidence_provider import (
    MACDEvidenceProvider,
)
from intelligence.evidence.providers.trend_evidence_provider import (
    TrendEvidenceProvider,
)

from intelligence.evidence.providers.market_structure_evidence_provider import (
    MarketStructureEvidenceProvider,
)
def create_default_evidence_manager() -> EvidenceManager:
    """
    Create the default evidence manager.
    """

    registry = EvidenceProviderRegistry()

    registry.register(
        EMAEvidenceProvider()
    )

    registry.register(
        RSIEvidenceProvider()
    )

    registry.register(
        MACDEvidenceProvider()
    )

    return EvidenceManager(registry)

