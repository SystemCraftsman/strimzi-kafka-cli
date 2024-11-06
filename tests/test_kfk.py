from importlib.metadata import version
from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.config import KUBECTL_VERSION, STRIMZI_VERSION


class TestKfk(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @mock.patch("kfk.setup.setup")
    def test_kfk(self, mock_setup):
        from kfk.main import kfk

        result = self.runner.invoke(kfk)
        assert result.exit_code == 0
        mock_setup.assert_called()

    @mock.patch("kfk.setup.setup")
    def test_kfk_version(self, mock_setup):
        from kfk.main import kfk

        result = self.runner.invoke(kfk, ["--version"])
        assert result.exit_code == 0
        cli_version = version("strimzi-kafka-cli")
        expected_version = f"""CLI Version: {cli_version}
Strimzi Version: {STRIMZI_VERSION}
Kubectl Version: {KUBECTL_VERSION}
"""

        assert result.output == expected_version
