from unittest import TestCase, mock
from click.testing import CliRunner
from kfk.connect_command import kfk
from kfk.kubectl_command_builder import Kubectl


class TestKfkConnect(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-connect-cluster"
        self.namespace = "kafka"
        self.replica_count = 3
        self.connect_config_file = "files/connect.properties"
        self.connector_config_file_1 = "files/connector1.properties"
        self.connector_config_file_2 = "files/connector2.properties"

    def test_no_option(self):
        result = self.runner.invoke(kfk, ['connect', '-n', self.namespace])
        assert result.exit_code == 0
        assert "Missing options: kfk connect" in result.output

    @mock.patch('kfk.connect_command.os')
    def test_create_cluster(self, mock_os):
        result = self.runner.invoke(kfk,
                                    ['connect', '--create', '--cluster', self.cluster, self.connect_config_file,
                                     '-n', self.namespace])
        assert result.exit_code == 0

    @mock.patch('kfk.connect_command.os')
    def test_create_cluster_three_replicas(self, mock_os):
        result = self.runner.invoke(kfk,
                                    ['connect', '--create', '--cluster', self.cluster, '--replica-count',
                                     self.replica_count, self.connect_config_file, '-n', self.namespace])
        assert result.exit_code == 0

    @mock.patch('kfk.connect_command.os')
    def test_create_cluster_with_connector_config(self, mock_os):
        result = self.runner.invoke(kfk,
                                    ['connect', '--create', '--cluster', self.cluster, self.connect_config_file,
                                     self.connector_config_file_1, self.connector_config_file_2, '-n', self.namespace])
        assert result.exit_code == 0

    @mock.patch('kfk.connect_command.os')
    def test_create_cluster_with_two_connectors_config(self, mock_os):
        result = self.runner.invoke(kfk,
                                    ['connect', '--create', '--cluster', self.cluster, self.connect_config_file,
                                     self.connector_config_file_1, '-n', self.namespace])
        assert result.exit_code == 0
