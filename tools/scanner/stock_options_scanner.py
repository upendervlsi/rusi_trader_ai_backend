"""
============================================================
RUSI Trader AI

Stock Options Scanner

Stage-4 adapter between the stock market-data collector
and the generic ScannerEngine interface.

This module does not perform bullish/bearish analysis or
option-contract selection yet.
============================================================
"""

from __future__ import annotations

from tools.scanner.scanner_models import (
    ScannerCandidate,
    ScannerRequest,
    ScannerResult,
)
from tools.scanner.stock_market_scanner import StockMarketScanner


class StockOptionsScanner:
    """
    ScannerEngine-compatible adapter for stock-options scanning.

    Stage 4 responsibility:
        ScannerRequest
            ↓
        StockMarketScanner
            ↓
        ScannerResult

    Direction, score, confidence and option selection are
    intentionally left for later stages.
    """

    def scan(
        self,
        request: ScannerRequest,
    ) -> ScannerResult:
        """
        Collect stock market data and expose it through the
        generic ScannerResult model.
        """

        parameters = dict(request.parameters)

        history_days = parameters.get("history_days")
        interval = parameters.get("interval")
        request_delay_seconds = parameters.get(
            "request_delay_seconds"
        )

        if history_days is None:
            return ScannerResult(
                scanner_type=request.scanner_type,
                success=False,
                messages=[
                    "Missing required scanner parameter: history_days"
                ],
            )

        if interval is None:
            return ScannerResult(
                scanner_type=request.scanner_type,
                success=False,
                messages=[
                    "Missing required scanner parameter: interval"
                ],
            )

        if request_delay_seconds is None:
            return ScannerResult(
                scanner_type=request.scanner_type,
                success=False,
                messages=[
                    "Missing required scanner parameter: "
                    "request_delay_seconds"
                ],
            )

        scanner = StockMarketScanner(
            history_days=history_days,
            interval=interval,
            request_delay_seconds=request_delay_seconds,
        )

        results = scanner.scan()

        if request.symbol:
            results = [
                result
                for result in results
                if result.get("symbol") == request.symbol
            ]

        candidates: list[ScannerCandidate] = []
        errors: list[dict] = []

        for result in results:

            symbol = result.get("symbol")

            if not symbol:
                continue

            if result.get("status") != "OK":
                errors.append(
                    {
                        "symbol": symbol,
                        "error": result.get(
                            "error",
                            "Unknown scanner error",
                        ),
                    }
                )
                continue

            exchange = result.get("exchange") or "NSE"

            metadata = dict(result)

            candidates.append(
                ScannerCandidate(
                    symbol=symbol,
                    exchange=exchange,
                    score=0.0,
                    confidence=0.0,
                    direction=None,
                    metadata=metadata,
                )
            )

        success_count = len(candidates)
        error_count = len(errors)

        messages = []

        if error_count:
            messages.append(
                f"{error_count} stock(s) failed during "
                "market-data collection"
            )

        return ScannerResult(
            scanner_type=request.scanner_type,
            success=error_count == 0,
            candidates=candidates,
            messages=messages,
            metadata={
                "stage": 4,
                "data_source": "StockMarketScanner",
                "universe_stock_count": scanner.universe.stock_count,
                "universe_contract_count": scanner.universe.contract_count,
                "requested_symbol": request.symbol,
                "timeframe": request.timeframe,
                "history_days": history_days,
                "interval": interval,
                "request_delay_seconds": request_delay_seconds,
                "successful_stock_count": success_count,
                "failed_stock_count": error_count,
                "errors": errors,
            },
        )
