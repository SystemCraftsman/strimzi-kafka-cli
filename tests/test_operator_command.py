from unittest import TestCase, mock
from click.testing import CliRunner
from kfk.commands.operator import kfk
from kfk.kubectl_command_builder import Kubectl
from kfk.config import STRIMZI_PATH


class TestKfkOperator(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"
        self.installation_file_count = 27

    @mock.patch('kfk.commands.operator.os.system')
    def test_install_strimzi(self, mock_os_system):
        result = self.runner.invoke(kfk, ['operator', '--install', '-n', self.namespace])
        assert result.exit_code == 0
        assert mock_os_system.call_count == self.installation_file_count
