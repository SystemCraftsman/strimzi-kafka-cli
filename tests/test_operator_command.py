from unittest import TestCase, mock
from click.testing import CliRunner
from kfk.operator_command import kfk
from kfk.kubectl_command_builder import Kubectl
from kfk.config import STRIMZI_PATH

class TestKfkOperator(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"
        self.operator_file_count = 22

    @mock.patch('kfk.operator_command.os.system')
    def test_install_strimzi(self, mock_os_system):
        result = self.runner.invoke(kfk, ['operator', '--install', '-n', self.namespace])
        assert result.exit_code == 0
        assert mock_os_system.call_count == self.operator_file_count
