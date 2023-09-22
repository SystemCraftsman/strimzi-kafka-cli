from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.config import KUBECTL_VERSION, STRIMZI_VERSION


class TestKfk(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @mock.patch("kfk.setup.setup")
    def test_kfk(self, mock_setup):
        from kfk.main import kfk as kfk_cli

        result = self.runner.invoke(kfk_cli)
        assert result.exit_code == 0
        mock_setup.assert_called()

    @mock.patch("kfk.setup.setup")
    def test_kfk_version(self, mock_setup):
        from kfk import __version__
        from kfk.main import kfk as kfk_cli

        result = self.runner.invoke(kfk_cli, ["--version"])
        assert result.exit_code == 0
        expected_version = f"""CLI Version: {__version__}
Strimzi Version: {STRIMZI_VERSION}
Kubectl Version: {KUBECTL_VERSION}
"""

        assert result.output == expected_version
