from tools.scanner.scanner_config import ScannerConfig
from tools.scanner.scanner_engine import ScannerEngine
from tools.scanner.scanner_manager import ScannerManager
from tools.scanner.scanner_models import (
    ScannerCandidate,
    ScannerRequest,
    ScannerResult,
)


class DummyScanner:

    def scan(
        self,
        request: ScannerRequest,
    ) -> ScannerResult:

        candidate = ScannerCandidate(
            symbol="SBIN",
            exchange="NSE",
            score=0.95,
            confidence=0.90,
        )

        return ScannerResult(
            scanner_type=request.scanner_type,
            success=True,
            candidates=[candidate],
        )


class InvalidScanner:
    pass


class ExceptionScanner:

    def scan(
        self,
        request: ScannerRequest,
    ) -> ScannerResult:
        raise RuntimeError("Scanner failure")


class TestScannerEngine:

    def setup_method(self):

        config = ScannerConfig(
            score_threshold=0.50,
            confidence_threshold=0.50,
        )

        manager = ScannerManager()

        self.engine = ScannerEngine(
            config=config,
            manager=manager,
        )

    # ---------------------------------------------------------

    def test_single_scanner(self):

        self.engine.manager.register_scanner(
            "equity",
            DummyScanner(),
        )

        result = self.engine.execute_scanner(
            ScannerRequest(scanner_type="equity")
        )

        assert result.success
        assert len(result.candidates) == 1

    # ---------------------------------------------------------

    def test_multiple_scanners(self):

        self.engine.manager.register_scanner(
            "equity",
            DummyScanner(),
        )

        requests = [
            ScannerRequest(scanner_type="equity"),
            ScannerRequest(scanner_type="equity"),
        ]

        results = self.engine.execute_scanners(requests)

        assert len(results) == 2

    # ---------------------------------------------------------

    def test_filter_candidates(self):

        candidate = ScannerCandidate(
            symbol="SBIN",
            exchange="NSE",
            score=0.90,
            confidence=0.90,
        )

        result = ScannerResult(
            scanner_type="equity",
            candidates=[candidate],
        )

        filtered = self.engine.filter_candidates(result)

        assert len(filtered.candidates) == 1

    # ---------------------------------------------------------

    def test_invalid_scanner(self):

        self.engine.manager.register_scanner(
            "invalid",
            InvalidScanner(),
        )

        result = self.engine.execute_scanner(
            ScannerRequest(scanner_type="invalid")
        )

        assert not result.success

    # ---------------------------------------------------------

    def test_exception_scanner(self):

        self.engine.manager.register_scanner(
            "exception",
            ExceptionScanner(),
        )

        result = self.engine.execute_scanner(
            ScannerRequest(scanner_type="exception")
        )

        assert not result.success

    # ---------------------------------------------------------

    def test_statistics(self):

        stats = self.engine.statistics()

        assert "enabled" in stats
        assert "registered_scanners" in stats

    # ---------------------------------------------------------

    def test_string_representation(self):

        value = str(self.engine)

        assert "ScannerEngine" in value
        assert value == repr(self.engine)

    # ---------------------------------------------------------

    def test_scan_pipeline(self):

        self.engine.manager.register_scanner(
            "equity",
            DummyScanner(),
        )

        result = self.engine.scan(
            [
                ScannerRequest(scanner_type="equity"),
            ]
        )

        assert result.success
        assert len(result.candidates) == 1

    # ---------------------------------------------------------

    def test_is_enabled(self):

        assert self.engine.is_enabled()
