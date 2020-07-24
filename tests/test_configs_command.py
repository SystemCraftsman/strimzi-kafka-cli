from unittest import TestCase, mock
from click.testing import CliRunner
from kfk.configs_command import kfk
from kfk.kubectl_command_builder import Kubectl


class TestKfkConfigs(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"
        self.topic = "my-topic"

    @mock.patch('kfk.configs_command.os')
    def test_configs(self, mock_os):
        result = self.runner.invoke(kfk, ['configs'])
        assert result.exit_code == 0