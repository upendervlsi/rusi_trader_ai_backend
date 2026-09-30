from datetime import datetime, timezone
from pathlib import Path

from backend.accounts.account_portfolio_store import (
    AccountPortfolioStore,
)
from intelligence.paper_trading.paper_portfolio import (
    PaperPortfolio,
)
from intelligence.paper_trading.paper_trade import (
    PaperTrade,
)
from intelligence.signals.signal_type import (
    SignalType,
)


def make_trade() -> PaperTrade:
    return PaperTrade(
        signal=SignalType.BUY,
        option_symbol="NIFTY26SEP25000CE",
        option_token="123456",
        exchange="NFO",
        strike=25000.0,
        expiry="2026-09-30",
        option_type="CE",
        entry_price=125.50,
        quantity=65,
        stop_loss=100.0,
        target_price=175.0,
        status="OPEN",
        pnl=0.0,
        current_price=140.0,
        reason="TEST",
        entry_time=datetime(
            2026,
            9,
            30,
            9,
            30,
            tzinfo=timezone.utc,
        ),
        exit_time=None,
    )


def test_missing_portfolio_returns_none(tmp_path: Path):
    store = AccountPortfolioStore(
        root=tmp_path
    )

    assert store.load("account_a") is None


def test_save_and_load_preserves_portfolio(tmp_path: Path):
    store = AccountPortfolioStore(
        root=tmp_path
    )

    trade = make_trade()

    portfolio = PaperPortfolio(
        capital=250000.0,
        available_capital=241833.5,
        realized_pnl=1833.5,
        open_trades=[trade],
        closed_trades=[],
    )

    store.save(
        "account_a",
        portfolio,
    )

    restored = store.load(
        "account_a"
    )

    assert restored is not None

    assert restored.capital == 250000.0
    assert restored.available_capital == 241833.5
    assert restored.realized_pnl == 1833.5

    assert len(restored.open_trades) == 1

    restored_trade = (
        restored.open_trades[0]
    )

    assert restored_trade.signal == SignalType.BUY
    assert restored_trade.option_symbol == (
        "NIFTY26SEP25000CE"
    )
    assert restored_trade.option_token == "123456"
    assert restored_trade.exchange == "NFO"
    assert restored_trade.strike == 25000.0
    assert restored_trade.expiry == "2026-09-30"
    assert restored_trade.option_type == "CE"
    assert restored_trade.entry_price == 125.50
    assert restored_trade.quantity == 65
    assert restored_trade.stop_loss == 100.0
    assert restored_trade.target_price == 175.0
    assert restored_trade.status == "OPEN"
    assert restored_trade.current_price == 140.0
    assert restored_trade.reason == "TEST"
    assert restored_trade.entry_time == trade.entry_time
    assert restored_trade.exit_time is None


def test_open_and_closed_trades_are_preserved(tmp_path: Path):
    store = AccountPortfolioStore(
        root=tmp_path
    )

    open_trade = make_trade()

    closed_trade = PaperTrade(
        signal=SignalType.SELL,
        option_symbol="NIFTY26SEP25000PE",
        option_token="654321",
        exchange="NFO",
        strike=25000.0,
        expiry="2026-09-30",
        option_type="PE",
        entry_price=150.0,
        quantity=65,
        stop_loss=180.0,
        target_price=110.0,
        status="TARGET",
        pnl=2600.0,
        current_price=110.0,
        reason="TARGET",
        entry_time=datetime(
            2026,
            9,
            30,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        exit_time=datetime(
            2026,
            9,
            30,
            11,
            0,
            tzinfo=timezone.utc,
        ),
    )

    portfolio = PaperPortfolio(
        capital=100000.0,
        available_capital=102600.0,
        realized_pnl=2600.0,
        open_trades=[open_trade],
        closed_trades=[closed_trade],
    )

    store.save(
        "account_a",
        portfolio,
    )

    restored = store.load(
        "account_a"
    )

    assert restored is not None
    assert len(restored.open_trades) == 1
    assert len(restored.closed_trades) == 1

    assert restored.closed_trades[0].signal == (
        SignalType.SELL
    )
    assert restored.closed_trades[0].pnl == 2600.0
    assert restored.closed_trades[0].status == "TARGET"


def test_accounts_are_persisted_separately(tmp_path: Path):
    store = AccountPortfolioStore(
        root=tmp_path
    )

    first = PaperPortfolio(
        capital=100000.0,
        available_capital=95000.0,
        realized_pnl=5000.0,
    )

    second = PaperPortfolio(
        capital=300000.0,
        available_capital=275000.0,
        realized_pnl=-25000.0,
    )

    store.save(
        "account_a",
        first,
    )

    store.save(
        "account_b",
        second,
    )

    restored_a = store.load(
        "account_a"
    )

    restored_b = store.load(
        "account_b"
    )

    assert restored_a is not None
    assert restored_b is not None

    assert restored_a.capital == 100000.0
    assert restored_a.realized_pnl == 5000.0

    assert restored_b.capital == 300000.0
    assert restored_b.realized_pnl == -25000.0


def test_portfolio_file_is_private(tmp_path: Path):
    store = AccountPortfolioStore(
        root=tmp_path
    )

    portfolio = PaperPortfolio(
        capital=100000.0,
        available_capital=100000.0,
    )

    store.save(
        "account_private",
        portfolio,
    )

    path = (
        tmp_path
        / "account_private"
        / "portfolio.json"
    )

    assert path.exists()
    assert (path.stat().st_mode & 0o777) == 0o600
