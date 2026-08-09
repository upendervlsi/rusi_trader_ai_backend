"""
============================================================

RUSI Trader AI

Analyzer Registry

============================================================
"""

from .trend_analyzer import TrendAnalyzer
from .momentum_analyzer import MomentumAnalyzer
from .options_analyzer import OptionsAnalyzer
from .volume_analyzer import VolumeAnalyzer


class AnalyzerRegistry:

    """
    Holds every analyzer used by
    the Intelligence Engine.
    """

    @staticmethod
    def get_analyzers():

        return [

            TrendAnalyzer(),

            MomentumAnalyzer(),

            OptionsAnalyzer(),

            VolumeAnalyzer(),

        ]
