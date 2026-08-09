"""
============================================================
RUSI Trader AI

Base Scanner

Shared functionality for all scanner implementations.
============================================================
"""

from __future__ import annotations

from tools.scanner.scanner_interface import ScannerInterface
from tools.scanner.scanner_models import (
    ScannerRequest,
    ScannerResult,
)


class BaseScanner(ScannerInterface):
    """
    Base implementation for all scanners.
    """

    scanner_name = "base"

    def scan(
        self,
        request: ScannerRequest,
    ) -> ScannerResult:
        """
        Default implementation.

        Derived scanners should override this method.
        """

        return ScannerResult(
            scanner_type=request.scanner_type,
            success=False,
            messages=[
                (
                    f"{self.__class__.__name__} "
                    "does not implement scan()."
                )
            ],
        )

    def supports(
        self,
        scanner_type: str,
    ) -> bool:
        """
        Returns True if this scanner supports
        the requested scanner type.
        """

        return scanner_type == self.scanner_name

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.scanner_name})"

    def __repr__(self) -> str:
        return self.__str__()
