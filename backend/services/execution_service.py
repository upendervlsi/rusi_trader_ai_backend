"""
============================================================

RUSI Trader AI

Execution Service

============================================================
"""

from backend.intelligence.execution_validator import (
    ExecutionValidator,
)


class ExecutionService:

    def __init__(self):

        self.validator = ExecutionValidator()

    # ------------------------------------------------------
    # Validate Trade Plan
    # ------------------------------------------------------

    def validate(

        self,

        trade_plan,

        runtime=None,

    ):

        return self.validator.validate(

            trade_plan,

            runtime,

        )
