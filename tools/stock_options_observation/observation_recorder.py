"""
RUSI Trader AI

Stock Options Observation Recorder

Stage 9

Purpose
-------
Convert an existing stock-option candidate decision into a
persisted observation.

This module does not change candidate selection, execution,
risk management, or the NIFTY V1 runtime.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from tools.scanner.stock_option_candidate_decision import (
    StockOptionCandidateDecision,
)

from .observation_models import StockOptionObservation
from .observation_writer import StockOptionsObservationWriter


class StockOptionsObservationRecorder:

    def __init__(
        self,
        writer: StockOptionsObservationWriter | None = None,
    ):

        self._writer = (
            writer
            if writer is not None
            else StockOptionsObservationWriter()
        )

    def record(
        self,
        decision: StockOptionCandidateDecision,
        stop_loss: float | None = None,
        target_price: float | None = None,
        risk_reward_ratio: float | None = None,
        maximum_loss: float | None = None,
        maximum_reward: float | None = None,
    ) -> StockOptionObservation:

        if decision is None:
            raise ValueError(
                "Stock-option candidate decision is required."
            )

        candidate = decision.candidate

        option_symbol = None
        option_type = None
        strike = None
        expiry = None
        token = None
        lot_size = None

        option_price = None
        quality_score = None
        quality_rank = None
        spread_percent = None
        volume = None
        open_interest = None
        volume_oi_ratio = None
        quote_completeness = None

        metadata = dict(decision.metadata)

        if candidate is not None:

            selected = candidate.candidate
            quality = candidate.quality

            option_symbol = selected.option_symbol
            option_type = selected.option_type
            strike = selected.strike
            expiry = selected.expiry
            token = selected.token
            lot_size = selected.lot_size

            option_price = quality.ltp
            quality_score = quality.quality_score
            quality_rank = quality.rank
            spread_percent = quality.spread_percent
            volume = quality.volume
            open_interest = quality.open_interest
            volume_oi_ratio = quality.volume_oi_ratio
            quote_completeness = quality.quote_completeness

        observation = StockOptionObservation(
            observation_id=str(uuid4()),
            observed_at=datetime.now(timezone.utc),
            symbol=decision.symbol,
            underlying_price=float(
                decision.underlying_price
            ),
            decision=decision.decision,
            direction=decision.direction,
            bullish_score=float(
                decision.bullish_score
            ),
            bearish_score=float(
                decision.bearish_score
            ),
            analysis_reason=decision.analysis_reason,
            option_symbol=option_symbol,
            option_type=option_type,
            strike=strike,
            expiry=expiry,
            token=token,
            lot_size=lot_size,
            option_price=option_price,
            quality_score=quality_score,
            quality_rank=quality_rank,
            spread_percent=spread_percent,
            volume=volume,
            open_interest=open_interest,
            volume_oi_ratio=volume_oi_ratio,
            quote_completeness=quote_completeness,
            stop_loss=stop_loss,
            target_price=target_price,
            risk_reward_ratio=risk_reward_ratio,
            maximum_loss=maximum_loss,
            maximum_reward=maximum_reward,
            metadata=metadata,
        )

        self._writer.append(observation)

        return observation
