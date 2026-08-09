"""
============================================================
RUSI Trader AI

Scanner Engine

Coordinates scanner registration, execution,
and result aggregation.
============================================================
"""

from __future__ import annotations

from tools.scanner.scanner_config import ScannerConfig
from tools.scanner.scanner_manager import ScannerManager
from tools.scanner.scanner_models import (
    ScannerRequest,
    ScannerResult,
)
from typing import Iterable

class ScannerEngine:
    """
    Central scanner execution engine.
    """

    def __init__(
        self,
        config: ScannerConfig | None = None,
        manager: ScannerManager | None = None,
    ) -> None:

        self.config = config or ScannerConfig()

        self.manager = manager or ScannerManager()
    # ---------------------------------------------------------

    def execute_scanner(
        self,
        request: ScannerRequest,
    ) -> ScannerResult:
        """
        Execute a single registered scanner.
        """

        scanner = self.manager.get_scanner(
            request.scanner_type
        )

        if scanner is None:
            return ScannerResult(
                scanner_type=request.scanner_type,
                success=False,
                messages=[
                    f"Scanner '{request.scanner_type}' is not registered."
                ],
            )

        return scanner.scan(request)
    # ---------------------------------------------------------

    def execute_scanners(
        self,
        requests: Iterable[ScannerRequest],
    ) -> list[ScannerResult]:
        """
        Execute multiple scanner requests sequentially.
        """

        results: list[ScannerResult] = []

        for request in requests:
            result = self.execute_scanner(request)
            results.append(result)

        return results
    # ---------------------------------------------------------

    def aggregate_results(
        self,
        results: Iterable[ScannerResult],
    ) -> ScannerResult:
        """
        Aggregate multiple scanner results into a single result.
        """

        aggregated = ScannerResult(
            scanner_type="aggregate",
            success=True,
        )

        for result in results:

            if not result.success:
                aggregated.success = False

            aggregated.candidates.extend(result.candidates)
            aggregated.messages.extend(result.messages)
            aggregated.metadata.update(result.metadata)

        return aggregated
    # ---------------------------------------------------------

    def filter_candidates(
        self,
        result: ScannerResult,
    ) -> ScannerResult:
        """
        Filter candidates using the configured score and
        confidence thresholds.
        """

        filtered = ScannerResult(
            scanner_type=result.scanner_type,
            success=result.success,
            messages=list(result.messages),
            metadata=dict(result.metadata),
        )

        for candidate in result.candidates:

            if (
                candidate.score >= self.config.score_threshold
                and candidate.confidence
                >= self.config.confidence_threshold
            ):
                filtered.candidates.append(candidate)

        return filtered
    # ---------------------------------------------------------

    def scan(
        self,
        requests: Iterable[ScannerRequest],
    ) -> ScannerResult:
        """
        Execute the complete scanning pipeline.

        Pipeline:
            Execute Scanners
                ↓
            Aggregate Results
                ↓
            Filter Candidates
        """

        results = self.execute_scanners(requests)

        aggregated = self.aggregate_results(results)

        filtered = self.filter_candidates(aggregated)

        return filtered
    # ---------------------------------------------------------

    def execute_scanner(
        self,
        request: ScannerRequest,
    ) -> ScannerResult:
        """
        Execute a single registered scanner.

        Any scanner exception is converted into a failed
        ScannerResult so that the remaining scanners can
        continue executing.
        """

        scanner = self.manager.get_scanner(
            request.scanner_type
        )

        if scanner is None:
            return ScannerResult(
                scanner_type=request.scanner_type,
                success=False,
                messages=[
                    f"Scanner '{request.scanner_type}' is not registered."
                ],
            )

        try:
            return scanner.scan(request)

        except Exception as ex:
            return ScannerResult(
                scanner_type=request.scanner_type,
                success=False,
                messages=[
                    f"Scanner execution failed: {ex}"
                ],
                metadata={
                    "exception": type(ex).__name__,
                },
            )
    # ---------------------------------------------------------

    def execute_scanner(
        self,
        request: ScannerRequest,
    ) -> ScannerResult:
        """
        Execute a single registered scanner.

        Validates the scanner interface before execution.
        """

        scanner = self.manager.get_scanner(
            request.scanner_type
        )

        if scanner is None:
            return ScannerResult(
                scanner_type=request.scanner_type,
                success=False,
                messages=[
                    f"Scanner '{request.scanner_type}' is not registered."
                ],
            )

        scan_method = getattr(scanner, "scan", None)

        if scan_method is None or not callable(scan_method):
            return ScannerResult(
                scanner_type=request.scanner_type,
                success=False,
                messages=[
                    (
                        f"Scanner '{request.scanner_type}' "
                        "does not implement scan()."
                    )
                ],
            )

        try:
            return scan_method(request)

        except Exception as ex:
            return ScannerResult(
                scanner_type=request.scanner_type,
                success=False,
                messages=[
                    f"Scanner execution failed: {ex}"
                ],
                metadata={
                    "exception": type(ex).__name__,
                },
            )
    # ---------------------------------------------------------

    def statistics(self) -> dict[str, object]:
        """
        Return basic runtime statistics for the scanner engine.
        """

        return {
            "enabled": self.config.enabled,
            "registered_scanners": len(
                self.manager.supported_scanner_types()
            ),
            "scanner_types": self.manager.supported_scanner_types(),
            "parallel_execution": self.config.parallel_scanners,
            "multi_timeframe": self.config.enable_multi_timeframe,
            "ai_ranking": self.config.enable_ai_ranking,
        }
    # ---------------------------------------------------------

    def __str__(self) -> str:
        """
        Return a human-readable representation of the scanner engine.
        """

        stats = self.statistics()

        return (
            "ScannerEngine("
            f"enabled={stats['enabled']}, "
            f"registered_scanners={stats['registered_scanners']}, "
            f"parallel_execution={stats['parallel_execution']})"
        )

    # ---------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return the official string representation.
        """

        return self.__str__()
    # ---------------------------------------------------------

    def is_enabled(self) -> bool:
        """
        Return whether the scanner engine is enabled.
        """

        return self.config.enabled
