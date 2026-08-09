"""
========================================================================

RUSI Trader AI

Evidence Provider Registry

Stores all registered evidence providers.

========================================================================
"""

from __future__ import annotations

from intelligence.evidence.evidence_provider import EvidenceProvider


class EvidenceProviderRegistry:
    """
    Registry of all evidence providers.
    """

    def __init__(self) -> None:

        self._providers: list[EvidenceProvider] = []

    # ---------------------------------------------------------

    def register(
        self,
        provider: EvidenceProvider,
    ) -> None:
        """
        Register one evidence provider.
        """

        self._providers.append(
            provider
        )

    # ---------------------------------------------------------

    @property
    def providers(
        self,
    ) -> list[EvidenceProvider]:
        """
        Return all registered providers.
        """

        return self._providers

    # ---------------------------------------------------------

    def count(
        self,
    ) -> int:
        """
        Number of registered providers.
        """

        return len(
            self._providers
        )
