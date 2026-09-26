"""
========================================================================

RUSI Trader AI

Default Evidence Registry

========================================================================

Creates the default EvidenceManager used by the trading runtime.

Registered providers
--------------------

1. EMA
2. RSI
3. MACD
4. Trend
5. Market Structure

Only providers implementing the current EvidenceProvider
interface are registered here.

========================================================================
"""

from __future__ import annotations

from intelligence.evidence.evidence_manager import (
    EvidenceManager,
)

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

    The provider order is intentional:

        EMA
        RSI
        MACD
        Trend
        MarketStructure

    All registered providers must implement the active
    EvidenceProvider.generate(feature_store, context) interface.
    """

    registry = EvidenceProviderRegistry()

    #
    # ---------------------------------------------------------
    # Technical Indicator Evidence
    # ---------------------------------------------------------
    #

    registry.register(
        EMAEvidenceProvider()
    )

    registry.register(
        RSIEvidenceProvider()
    )

    registry.register(
        MACDEvidenceProvider()
    )

    #
    # ---------------------------------------------------------
    # Market Structure Evidence
    # ---------------------------------------------------------
    #

    #
    # NOTE:
    # These providers require their corresponding engines.
    # They are therefore not registered here until the default
    # TrendEngine and MarketStructureEngine construction path
    # is confirmed.
    #
    # registry.register(
    #     TrendEvidenceProvider(
    #         trend_engine=...
    #     )
    # )
    #
    # registry.register(
    #     MarketStructureEvidenceProvider(
    #         structure_engine=...
    #     )
    # )

    return EvidenceManager(
        registry
    )
