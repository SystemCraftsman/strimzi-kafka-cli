from unittest import TestCase, mock

from click.testing import CliRunner


class TestKfkMcp(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @mock.patch("kfk.setup.setup")
    def test_mcp_command_registered(self, mock_setup):
        from kfk.main import kfk

        result = self.runner.invoke(kfk, ["mcp", "--help"])
        assert result.exit_code == 0
        assert "Starts the Strimzi MCP server" in result.output
