from types import SimpleNamespace
from datetime import datetime, timedelta, timezone

import pytest

from backend.services.sensex_paper_scheduler import (
    SensexPaperScheduler,
)

from tools.execution.sensex_paper_runtime import (
    SensexPaperRuntime,
)


class FakeNonPaperEngine:

    def is_paper_engine(self):
        return False


class FakePaperEngine:

    def is_paper_engine(self):
        return True


def test_sensex_runtime_rejects_non_paper_engine():

    with pytest.raises(
        ValueError,
        match="paper execution engine",
    ):

        SensexPaperRuntime(
            FakeNonPaperEngine(),
            SimpleNamespace(),
        )


def test_sensex_runtime_rejects_non_bfo_candidate():

    runtime = SensexPaperRuntime(
        FakePaperEngine(),
        SimpleNamespace(),
    )

    result = runtime.execute(
        {
            "symbol": "SENSEX",
            "direction": "BULLISH",
            "price": 100.0,
            "candidate": {
                "underlying": "SENSEX",
                "exchange": "NFO",
                "option_symbol": "SENSEXTESTCE",
                "option_type": "CE",
                "lot_size": 20,
            },
        }
    )

    assert result.success is False
    assert "BFO" in result.message


def test_sensex_runtime_rejects_wrong_underlying():

    runtime = SensexPaperRuntime(
        FakePaperEngine(),
        SimpleNamespace(),
    )

    result = runtime.execute(
        {
            "symbol": "SENSEX",
            "direction": "BULLISH",
            "price": 100.0,
            "candidate": {
                "underlying": "NIFTY",
                "exchange": "BFO",
                "option_symbol": "SENSEXTESTCE",
                "option_type": "CE",
                "lot_size": 20,
            },
        }
    )

    assert result.success is False
    assert "underlying" in result.message


def test_sensex_runtime_rejects_direction_option_mismatch():

    runtime = SensexPaperRuntime(
        FakePaperEngine(),
        SimpleNamespace(),
    )

    result = runtime.execute(
        {
            "symbol": "SENSEX",
            "direction": "BULLISH",
            "price": 100.0,
            "candidate": {
                "underlying": "SENSEX",
                "exchange": "BFO",
                "option_symbol": "SENSEXTESTPE",
                "option_type": "PE",
                "lot_size": 20,
            },
        }
    )

    assert result.success is False
    assert "mismatch" in result.message

def _fresh_sensex_pulse(**overrides):
    now = datetime.now(timezone.utc)

    values = {
        "market": "SENSEX_FNO",
        "signal": "BULLISH",
        "confidence": 0.85,
        "status": "LIVE",
        "last_price": 85000.0,
        "updated_time": now.isoformat(),
    }

    values.update(overrides)

    return SimpleNamespace(**values)


def test_sensex_freshness_accepts_fresh_live_pulse():
    scheduler = SensexPaperScheduler()

    ok, message = scheduler._validate_fresh_sensex_pulse(
        _fresh_sensex_pulse()
    )

    assert ok is True
    assert "Fresh SENSEX pulse" in message


def test_sensex_freshness_rejects_stale_pulse():
    scheduler = SensexPaperScheduler()

    stale_time = (
        datetime.now(timezone.utc)
        - timedelta(
            seconds=SensexPaperScheduler.MAX_PULSE_AGE_SECONDS + 1
        )
    ).isoformat()

    ok, message = scheduler._validate_fresh_sensex_pulse(
        _fresh_sensex_pulse(
            updated_time=stale_time,
        )
    )

    assert ok is False
    assert "stale" in message.lower()


def test_sensex_freshness_rejects_waiting_status():
    scheduler = SensexPaperScheduler()

    ok, message = scheduler._validate_fresh_sensex_pulse(
        _fresh_sensex_pulse(
            status="WAITING",
        )
    )

    assert ok is False
    assert "not LIVE" in message


def test_sensex_freshness_rejects_missing_timestamp():
    scheduler = SensexPaperScheduler()

    ok, message = scheduler._validate_fresh_sensex_pulse(
        _fresh_sensex_pulse(
            updated_time=None,
        )
    )

    assert ok is False
    assert "updated_time is missing" in message


def test_sensex_freshness_rejects_invalid_price():
    scheduler = SensexPaperScheduler()

    ok, message = scheduler._validate_fresh_sensex_pulse(
        _fresh_sensex_pulse(
            last_price=0,
        )
    )

    assert ok is False
    assert "last_price is invalid" in message


def test_sensex_freshness_rejects_future_timestamp():
    scheduler = SensexPaperScheduler()

    future_time = (
        datetime.now(timezone.utc)
        + timedelta(seconds=10)
    ).isoformat()

    ok, message = scheduler._validate_fresh_sensex_pulse(
        _fresh_sensex_pulse(
            updated_time=future_time,
        )
    )

    assert ok is False
    assert "future" in message.lower()


def test_sensex_freshness_rejects_invalid_signal():
    scheduler = SensexPaperScheduler()

    ok, message = scheduler._validate_fresh_sensex_pulse(
        _fresh_sensex_pulse(
            signal="WAIT",
        )
    )

    assert ok is False
    assert "not entry eligible" in message

