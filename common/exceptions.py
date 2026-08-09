"""
============================================================

Custom Exceptions

============================================================
"""


class RusiTraderException(Exception):
    """
    Base exception for the project.
    """
    pass


class DataSourceError(RusiTraderException):
    """
    Raised when broker communication fails.
    """
    pass


class LoaderError(RusiTraderException):
    """
    Raised when a loader cannot retrieve or parse data.
    """
    pass


class ValidationError(RusiTraderException):
    """
    Raised when market data validation fails.
    """
    pass
