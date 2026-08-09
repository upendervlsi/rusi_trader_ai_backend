from __future__ import annotations

from pathlib import Path
from typing import Dict, List
class ScannerManager:
    """
    Central manager responsible for coordinating
    multi-instrument market scanning.
    """

    def __init__(self):
        """
        Initialize scanner manager.
        """

        self._registered_scanners: Dict[str, object] = {}
    # ---------------------------------------------------------

    def register_scanner(
        self,
        scanner_type: str,
        scanner: object,
    ) -> None:
        """
        Register a scanner implementation.
        """

        self._registered_scanners[scanner_type] = scanner
    # ---------------------------------------------------------

    def get_scanner(
        self,
        scanner_type: str,
    ) -> object | None:
        """
        Return the registered scanner for the
        requested scanner type.
        """

        return self._registered_scanners.get(scanner_type)
    # ---------------------------------------------------------

    def supported_scanner_types(
        self,
    ) -> List[str]:
        """
        Return all registered scanner types.
        """

        return sorted(self._registered_scanners.keys())
    # ---------------------------------------------------------

    def has_scanner(
        self,
        scanner_type: str,
    ) -> bool:
        """
        Return True if a scanner has been registered
        for the specified scanner type.
        """

        return scanner_type in self._registered_scanners
    # ---------------------------------------------------------

    def unregister_scanner(
        self,
        scanner_type: str,
    ) -> bool:
        """
        Unregister a scanner.

        Returns
        -------
        bool
            True if the scanner existed and was removed,
            otherwise False.
        """

        if scanner_type not in self._registered_scanners:
            return False

        del self._registered_scanners[scanner_type]
        return True
    # ---------------------------------------------------------

    def clear_scanners(self) -> None:
        """
        Remove all registered scanners.
        """

        self._registered_scanners.clear()
    # ---------------------------------------------------------

    def __str__(self) -> str:
        """
        Return a human-readable description of the scanner manager.
        """

        return (
            f"ScannerManager("
            f"registered_scanners={len(self._registered_scanners)})"
        )

    # ---------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return the official string representation.
        """

        return self.__str__()
from tools.scanner.scanner_manager import ScannerManager


class TestScannerManager:

    def setup_method(self):
        self.manager = ScannerManager()

    # ---------------------------------------------------------

    def test_scanner_registry(self):

        dummy_scanner = object()

        self.manager.register_scanner(
            "equity",
            dummy_scanner,
        )

        assert self.manager.has_scanner("equity")

        assert (
            self.manager.get_scanner("equity")
            is dummy_scanner
        )

        assert (
            self.manager.supported_scanner_types()
            == ["equity"]
        )

    # ---------------------------------------------------------

    def test_unregister_scanner(self):

        self.manager.register_scanner(
            "equity",
            object(),
        )

        assert self.manager.unregister_scanner(
            "equity"
        )

        assert not self.manager.has_scanner(
            "equity"
        )

    # ---------------------------------------------------------

    def test_clear_scanners(self):

        self.manager.register_scanner(
            "equity",
            object(),
        )

        self.manager.register_scanner(
            "options",
            object(),
        )

        self.manager.clear_scanners()

        assert (
            self.manager.supported_scanner_types()
            == []
        )

    # ---------------------------------------------------------

    def test_string_representation(self):

        value = str(self.manager)

        assert "ScannerManager" in value

        assert value == repr(self.manager)
