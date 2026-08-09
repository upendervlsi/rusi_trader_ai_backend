from dataclasses import dataclass, field


@dataclass(slots=True)
class ExecutionPolicyResult:

    trade_allowed: bool

    reason: str

    warnings: list[str] = field(default_factory=list)
