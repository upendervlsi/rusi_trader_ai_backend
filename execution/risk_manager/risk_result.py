from dataclasses import dataclass, field


@dataclass(slots=True)
class RiskResult:

    trade_allowed: bool

    reason: str

    approved_quantity: int

    warnings: list[str] = field(default_factory=list)
