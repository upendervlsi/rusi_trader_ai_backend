"""
RUSI Trader AI

Stock Options Observation Writer

Stage 9

Purpose
-------
Append stock-options observations to an isolated CSV file.

This writer does not modify the existing NIFTY V1 trade journal.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .observation_models import StockOptionObservation


class StockOptionsObservationWriter:

    def __init__(
        self,
        output_file: Path | None = None,
    ):

        self._file = (
            output_file
            if output_file is not None
            else Path("runs") / "stock_options" / "observations.csv"
        )

        self._file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self._file.exists():

            with self._file.open(
                "w",
                newline="",
                encoding="utf-8",
            ) as fp:

                writer = csv.writer(fp)

                writer.writerow([
                    "ObservationID",
                    "ObservedAt",
                    "Symbol",
                    "UnderlyingPrice",
                    "Decision",
                    "Direction",
                    "BullishScore",
                    "BearishScore",
                    "AnalysisReason",
                    "OptionSymbol",
                    "OptionType",
                    "Strike",
                    "Expiry",
                    "Token",
                    "LotSize",
                    "OptionPrice",
                    "QualityScore",
                    "QualityRank",
                    "SpreadPercent",
                    "Volume",
                    "OpenInterest",
                    "VolumeOIRatio",
                    "QuoteCompleteness",
                    "StopLoss",
                    "TargetPrice",
                    "RiskRewardRatio",
                    "MaximumLoss",
                    "MaximumReward",
                    "Metadata",
                ])

    def append(
        self,
        observation: StockOptionObservation,
    ) -> None:

        with self._file.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as fp:

            writer = csv.writer(fp)

            writer.writerow([
                observation.observation_id,
                observation.observed_at.isoformat(),
                observation.symbol,
                observation.underlying_price,
                observation.decision,
                observation.direction,
                observation.bullish_score,
                observation.bearish_score,
                observation.analysis_reason,
                observation.option_symbol,
                observation.option_type,
                observation.strike,
                observation.expiry,
                observation.token,
                observation.lot_size,
                observation.option_price,
                observation.quality_score,
                observation.quality_rank,
                observation.spread_percent,
                observation.volume,
                observation.open_interest,
                observation.volume_oi_ratio,
                observation.quote_completeness,
                observation.stop_loss,
                observation.target_price,
                observation.risk_reward_ratio,
                observation.maximum_loss,
                observation.maximum_reward,
                json.dumps(
                    observation.metadata,
                    separators=(",", ":"),
                    default=str,
                ),
            ])
