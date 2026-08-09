"""
============================================================

RUSI Trader AI

Analyzer Pipeline

Executes all registered analyzers.

============================================================
"""

from typing import List

from .base_analyzer import BaseAnalyzer
from .analyzer_result import AnalyzerResult


class AnalyzerPipeline:

    """
    Executes all analyzers in sequence.
    """

    def __init__(self) -> None:

        self._analyzers: List[BaseAnalyzer] = []

    # ------------------------------------------------------
    # Register Analyzer
    # ------------------------------------------------------

    def register(
        self,
        analyzer: BaseAnalyzer,
    ) -> None:

        self._analyzers.append(analyzer)

    # ------------------------------------------------------
    # Execute
    # ------------------------------------------------------

    def execute(
        self,
        **kwargs,
    ) -> List[AnalyzerResult]:

        results: List[AnalyzerResult] = []

        for analyzer in self._analyzers:

            result = analyzer.analyze(**kwargs)

            results.append(result)

        return results
