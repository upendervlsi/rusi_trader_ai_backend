"""
RUSI Trader AI

Stock Options Observation Runner

Stage 9

Runs the complete dynamically discovered stock-options
observation workflow.

This runner:
    - scans the complete stock-options underlying universe
    - passes successful stock scans to the observation orchestrator
    - records observations through the existing writer
    - produces a run-level summary

This module does NOT:
    - place broker orders
    - modify NIFTY V1
    - modify strategy thresholds
    - hardcode stocks, strikes, expiries, or lot sizes
"""

from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Any

from tools.scanner.stock_market_scanner import (
    StockMarketScanner,
)
from tools.stock_options_observation.observation_orchestrator import (
    StockOptionsObservationOrchestrator,
)


@dataclass(slots=True)
class StockOptionsObservationRunResult:
    success: bool
    elapsed_seconds: float
    scanned_stocks: int
    successful_scans: int
    failed_scans: int
    observations_recorded: int
    candidate_count: int
    no_trade_count: int
    risk_allowed_count: int
    risk_rejected_count: int
    errors: list[dict[str, Any]]


class StockOptionsObservationRunner:

    def __init__(
        self,
        history_days: int,
        interval: str,
        market_request_delay_seconds: float,
        option_request_delay_seconds: float,
    ):

        if history_days <= 0:
            raise ValueError(
                "history_days must be greater than zero."
            )

        if not interval:
            raise ValueError(
                "interval must not be empty."
            )

        if market_request_delay_seconds < 0:
            raise ValueError(
                "market_request_delay_seconds must not be negative."
            )

        if option_request_delay_seconds < 0:
            raise ValueError(
                "option_request_delay_seconds must not be negative."
            )

        self._market_scanner = StockMarketScanner(
            history_days=history_days,
            interval=interval,
            request_delay_seconds=market_request_delay_seconds,
        )

        self._orchestrator = (
            StockOptionsObservationOrchestrator(
                market_scanner=self._market_scanner,
                request_delay_seconds=option_request_delay_seconds,
            )
        )

    def run(
        self,
        symbols: list[str] | None = None,
    ) -> StockOptionsObservationRunResult:

        started = monotonic()

        if symbols is None:
            results = self._market_scanner.scan()
        else:
            normalized_symbols = [
                str(symbol).strip().upper()
                for symbol in symbols
                if str(symbol).strip()
            ]

            if not normalized_symbols:
                results = []
            else:
                results = self._market_scanner.scan_symbols(
                    normalized_symbols
                )

        scanned_stocks = len(results)
        successful_scans = 0
        failed_scans = 0
        observations_recorded = 0

        candidate_count = 0
        no_trade_count = 0
        risk_allowed_count = 0
        risk_rejected_count = 0

        errors: list[dict[str, Any]] = []

        for scan_result in results:

            if scan_result.get("status") != "OK":

                failed_scans += 1

                errors.append(
                    {
                        "symbol": scan_result.get("symbol"),
                        "status": scan_result.get("status"),
                        "error": scan_result.get("error"),
                    }
                )

                continue

            successful_scans += 1

            try:

                observation = (
                    self._orchestrator.observe_stock(
                        scan_result
                    )
                )

                if observation is None:
                    continue

                observations_recorded += 1

                decision = str(
                    observation.decision
                ).upper()

                if decision == "CANDIDATE":
                    candidate_count += 1

                elif decision == "NO_TRADE":
                    no_trade_count += 1

                metadata = (
                    observation.metadata or {}
                )

                risk = metadata.get(
                    "risk",
                    {},
                )

                if risk.get("risk_evaluated"):

                    if risk.get("risk_allowed"):
                        risk_allowed_count += 1
                    else:
                        risk_rejected_count += 1

            except Exception as exc:

                errors.append(
                    {
                        "symbol": scan_result.get("symbol"),
                        "status": "OBSERVATION_ERROR",
                        "error": str(exc),
                    }
                )

        elapsed_seconds = (
            monotonic() - started
        )

        return StockOptionsObservationRunResult(
            success=(
                successful_scans > 0
                and not any(
                    error.get("status")
                    == "OBSERVATION_ERROR"
                    for error in errors
                )
            ),
            elapsed_seconds=elapsed_seconds,
            scanned_stocks=scanned_stocks,
            successful_scans=successful_scans,
            failed_scans=failed_scans,
            observations_recorded=observations_recorded,
            candidate_count=candidate_count,
            no_trade_count=no_trade_count,
            risk_allowed_count=risk_allowed_count,
            risk_rejected_count=risk_rejected_count,
            errors=errors,
        )
