from tools.scanner.equity_scanner import EquityScanner
from tools.scanner.scanner_models import ScannerRequest


class TestEquityScanner:

    def setup_method(self):

        self.scanner = EquityScanner()

    # ---------------------------------------------------------

    def test_scanner_name(self):

        assert self.scanner.scanner_name == "equity"

    # ---------------------------------------------------------

    def test_supported_exchanges(self):

        exchanges = self.scanner.supported_exchanges()

        assert "NSE" in exchanges
        assert "BSE" in exchanges

    # ---------------------------------------------------------

    def test_validate_request_success(self):

        request = ScannerRequest(
            scanner_type="equity",
            symbol="SBIN",
        )

        assert self.scanner.validate_request(request)

    # ---------------------------------------------------------

    def test_validate_request_failure(self):

        request = ScannerRequest(
            scanner_type="equity",
        )

        assert not self.scanner.validate_request(request)

    # ---------------------------------------------------------

    def test_scan_with_symbol(self):

        request = ScannerRequest(
            scanner_type="equity",
            symbol="SBIN",
            exchange="NSE",
        )

        result = self.scanner.scan(request)

        assert result.success
        assert len(result.candidates) == 1

        candidate = result.candidates[0]

        assert candidate.symbol == "SBIN"
        assert candidate.exchange == "NSE"

    # ---------------------------------------------------------

    def test_scan_without_symbol(self):

        request = ScannerRequest(
            scanner_type="equity",
        )

        result = self.scanner.scan(request)

        assert result.success
        assert len(result.candidates) == 0
        assert len(result.messages) == 1

    # ---------------------------------------------------------

    def test_string_representation(self):

        value = str(self.scanner)

        assert "EquityScanner" in value
        assert value == repr(self.scanner)
