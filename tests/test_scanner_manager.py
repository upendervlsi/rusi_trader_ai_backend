from tools.scanner.scanner_manager import ScannerManager


class TestScannerManager:

    def setup_method(self):
        self.manager = ScannerManager()

    # ---------------------------------------------------------

    def test_scanner_registry(self):

        dummy_scanner = object()

        self.manager.register_scanner(
            "equity",
            dummy_scanner,
        )

        assert self.manager.has_scanner("equity")

        assert (
            self.manager.get_scanner("equity")
            is dummy_scanner
        )

        assert (
            self.manager.supported_scanner_types()
            == ["equity"]
        )

    # ---------------------------------------------------------

    def test_unregister_scanner(self):

        self.manager.register_scanner(
            "equity",
            object(),
        )

        assert self.manager.unregister_scanner(
            "equity"
        )

        assert not self.manager.has_scanner(
            "equity"
        )

    # ---------------------------------------------------------

    def test_clear_scanners(self):

        self.manager.register_scanner(
            "equity",
            object(),
        )

        self.manager.register_scanner(
            "options",
            object(),
        )

        self.manager.clear_scanners()

        assert (
            self.manager.supported_scanner_types()
            == []
        )

    # ---------------------------------------------------------

    def test_string_representation(self):

        value = str(self.manager)

        assert "ScannerManager" in value

        assert value == repr(self.manager)
