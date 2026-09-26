"""
============================================================

RUSI Trader AI

Trading Runtime Manager

Singleton runtime manager.

The runtime manager publishes one complete runtime
state for each successfully processed trading cycle.

Backward compatibility:
    - Existing get_state() behavior is preserved.
    - Existing update() behavior is preserved.
    - Existing NIFTY V1 runtime path remains unchanged.

Market isolation:
    - Additional market-specific runtime states can be
      published and retrieved independently.
    - MIDCAP can therefore have its own runtime state
      without replacing the existing default state.
============================================================
"""

from __future__ import annotations

from threading import Lock
from typing import Any

from trading.runtime.runtime_state import (
    TradingRuntimeState,
)


class RuntimeManager:

    _instance = None

    _lock = Lock()

    # ---------------------------------------------------------
    # Singleton
    # ---------------------------------------------------------

    def __new__(cls):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

                cls._instance.state = (
                    TradingRuntimeState()
                )

                cls._instance._cycle_id = 0

                # -------------------------------------------------
                # Market-specific runtime states.
                #
                # Existing state remains the backward-compatible
                # default runtime state.
                #
                # New isolated markets are stored here.
                # -------------------------------------------------

                cls._instance._market_states = {}

                # -------------------------------------------------
                # Current Market Data Engine
                #
                # This is a runtime dependency, not part of the
                # serializable TradingRuntimeState.
                # -------------------------------------------------

                cls._instance._market_data_engine = None

        return cls._instance

    # ---------------------------------------------------------
    # Get Runtime State
    # ---------------------------------------------------------

    def get_state(
        self,
    ) -> TradingRuntimeState:

        return self.state

    # ---------------------------------------------------------
    # Market-Specific Runtime State
    # ---------------------------------------------------------

    def get_state_for_market(
        self,
        market_name: str,
    ) -> TradingRuntimeState:
        """
        Return the runtime state for a specific logical market.

        This method does not affect the existing default
        runtime state returned by get_state().
        """

        if not market_name:
            raise ValueError(
                "Market name cannot be empty."
            )

        state = self._market_states.get(
            market_name
        )

        if state is None:

            state = TradingRuntimeState()

            self._market_states[
                market_name
            ] = state

        return state

    # ---------------------------------------------------------
    # Market Data Engine
    # ---------------------------------------------------------

    def set_market_data_engine(
        self,
        market_data_engine,
    ) -> None:

        self._market_data_engine = (
            market_data_engine
        )

    def get_market_data_engine(self):

        return self._market_data_engine

    # ---------------------------------------------------------
    # Internal State Builder
    # ---------------------------------------------------------

    def _build_next_state(
        self,
        previous_state: TradingRuntimeState,
        cycle_id: int,
        **kwargs: Any,
    ) -> TradingRuntimeState:
        """
        Build a complete next runtime state.

        This follows the same state-preservation behavior
        used by the original update() implementation.
        """

        valid_fields = set(
            TradingRuntimeState.__dataclass_fields__.keys()
        )

        unknown_fields = (
            set(kwargs.keys()) - valid_fields
        )

        if unknown_fields:

            raise ValueError(
                "Unknown runtime state fields: "
                + ", ".join(
                    sorted(unknown_fields)
                )
            )

        # -----------------------------------------------------
        # Start from previous state.
        #
        # This preserves fields that are not supplied in
        # the current update.
        # -----------------------------------------------------

        state_values = {}

        for field_name in valid_fields:

            state_values[field_name] = getattr(
                previous_state,
                field_name,
            )

        # -----------------------------------------------------
        # Apply new runtime values.
        # -----------------------------------------------------

        for key, value in kwargs.items():

            state_values[key] = value

        # -----------------------------------------------------
        # Runtime cycle ID.
        # -----------------------------------------------------

        state_values["cycle_id"] = cycle_id

        # -----------------------------------------------------
        # Data status.
        # -----------------------------------------------------

        if "data_status" not in kwargs:

            if kwargs.get("snapshot") is not None:

                state_values["data_status"] = (
                    "HISTORICAL"
                )

        # -----------------------------------------------------
        # Create complete next state.
        # -----------------------------------------------------

        return TradingRuntimeState(
            **state_values
        )

    # ---------------------------------------------------------
    # Publish Runtime State
    # ---------------------------------------------------------

    def update(
        self,
        **kwargs: Any,
    ) -> None:
        """
        Publish one completed trading cycle to the existing
        default runtime state.

        This method intentionally preserves the original
        behavior used by the existing NIFTY V1 runtime.
        """

        next_cycle_id = (
            self._cycle_id + 1
        )

        next_state = self._build_next_state(
            self.state,
            next_cycle_id,
            **kwargs,
        )

        # -----------------------------------------------------
        # Publish complete state.
        # -----------------------------------------------------

        self.state = next_state

        self._cycle_id = (
            next_cycle_id
        )

    # ---------------------------------------------------------
    # Publish Market-Specific Runtime State
    # ---------------------------------------------------------

    def update_for_market(
        self,
        market_name: str,
        **kwargs: Any,
    ) -> None:
        """
        Publish one completed trading cycle for a specific
        logical market.

        This does NOT replace the existing default runtime
        state and does NOT modify update().
        """

        if not market_name:
            raise ValueError(
                "Market name cannot be empty."
            )

        previous_state = (
            self._market_states.get(
                market_name
            )
        )

        if previous_state is None:

            previous_state = (
                TradingRuntimeState()
            )

        next_cycle_id = (
            previous_state.cycle_id + 1
        )

        next_state = self._build_next_state(
            previous_state,
            next_cycle_id,
            **kwargs,
        )

        self._market_states[
            market_name
        ] = next_state

    # ---------------------------------------------------------
    # Available Market States
    # ---------------------------------------------------------

    def get_available_markets(self) -> list[str]:
        """
        Return logical markets that currently have an
        isolated runtime state.
        """

        return sorted(
            self._market_states.keys()
        )
