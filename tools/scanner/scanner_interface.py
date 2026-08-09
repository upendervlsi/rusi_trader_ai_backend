"""
============================================================
RUSI Trader AI

Scanner Interface

Defines the common contract implemented by every scanner.
============================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from tools.scanner.scanner_models import (
    ScannerRequest,
    ScannerResult,
)


class ScannerInterface(ABC):
    """
    Common interface for all scanner implementations.
    """

    @abstractmethod
    def scan(
        self,
        request: ScannerRequest,
    ) -> ScannerResult:
        """
        Execute the scanner.
        """
        raise NotImplementedError
