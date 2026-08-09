"""
========================================================================

RUSI Trader AI

Evidence Provider Factory

Description
-----------
Creates the complete list of evidence providers used by the
EvidenceManager.

========================================================================
"""

from __future__ import annotations

from intelligence.evidence.base_evidence_provider import (
    BaseEvidenceProvider,
)


def create_default_providers() -> list[BaseEvidenceProvider]:
    """
    Returns all default evidence providers.

    Initially empty.

    Providers will be added incrementally.
    """

    providers: list[BaseEvidenceProvider] = []

    #
    # Future
    #
    # providers.append(MACDEvidenceProvider())
    # providers.append(RSIEvidenceProvider())
    #

    return providers
