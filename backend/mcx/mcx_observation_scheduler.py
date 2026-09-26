from __future__ import annotations

import sys
from datetime import datetime

from backend.mcx.mcx_observation_runner import run_observation_cycle


def main() -> int:
    started = datetime.now().isoformat(timespec="seconds")
    print(f"[MCX OBSERVER] START {started}", flush=True)

    try:
        run_observation_cycle()

        print(
            "[MCX OBSERVER] CYCLE SUCCESS",
            flush=True,
        )

        return 0

    except Exception as exc:
        print(
            f"[MCX OBSERVER] ERROR: "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
            flush=True,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
