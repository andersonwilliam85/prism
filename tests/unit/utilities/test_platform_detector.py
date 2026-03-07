"""Tests for prism.utilities.platform_detector."""

from unittest.mock import patch, mock_open

from prism.utilities.platform_detector import detect_platform


class TestDetectPlatform:
    @patch("prism.utilities.platform_detector.platform")
    def test_mac_arm64(self, mock_plat):
        mock_plat.system.return_value = "Darwin"
        mock_plat.machine.return_value = "arm64"
        assert detect_platform() == ("mac", "Apple Silicon")

    @patch("prism.utilities.platform_detector.platform")
    def test_mac_intel(self, mock_plat):
        mock_plat.system.return_value = "Darwin"
        mock_plat.machine.return_value = "x86_64"
        assert detect_platform() == ("mac", "Intel")

    @patch("prism.utilities.platform_detector.platform")
    def test_windows(self, mock_plat):
        mock_plat.system.return_value = "Windows"
        mock_plat.version.return_value = "10.0.19041"
        assert detect_platform() == ("windows", "10.0.19041")

    @patch(
        "builtins.open",
        mock_open(read_data="NAME=Ubuntu\nVERSION=22.04"),
    )
    @patch("prism.utilities.platform_detector.platform")
    def test_ubuntu(self, mock_plat):
        mock_plat.system.return_value = "Linux"
        mock_plat.version.return_value = "5.15"
        assert detect_platform() == ("ubuntu", "5.15")

    @patch("prism.utilities.platform_detector.platform")
    def test_linux_non_ubuntu(self, mock_plat):
        mock_plat.system.return_value = "Linux"
        mock_plat.version.return_value = "5.15"
        with patch("builtins.open", mock_open(read_data="NAME=Fedora")):
            assert detect_platform() == ("linux", "5.15")

    @patch("prism.utilities.platform_detector.platform")
    def test_unknown(self, mock_plat):
        mock_plat.system.return_value = "FreeBSD"
        assert detect_platform() == ("unknown", "")
