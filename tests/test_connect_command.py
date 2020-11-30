from unittest import TestCase, mock
from click.testing import CliRunner
from kfk.connect_command import kfk
from kfk.kubectl_command_builder import Kubectl


class TestKfkConnect(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"

    def test_no_option(self):
        result = self.runner.invoke(kfk, ['connect', '-n', self.namespace])
        assert result.exit_code == 0
        assert "Missing options: kfk connect" in result.output
