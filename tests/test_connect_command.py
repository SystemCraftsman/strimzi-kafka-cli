from unittest import TestCase, mock
from click.testing import CliRunner
from kfk.commands.connect import kfk
from kfk.kubectl_command_builder import Kubectl


class TestKfkConnect(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-connect-cluster"
        self.namespace = "kafka"
        self.connect_config_file = "files/connect.properties"
        self.connector_config_file_1 = "files/connector1.properties"
        self.connector_config_file_2 = "files/connector2.properties"

    def test_no_option(self):
        result = self.runner.invoke(kfk, ['connect', '-n', self.namespace])
        assert result.exit_code == 0
        assert "Missing options: kfk connect" in result.output

    @mock.patch('kfk.commands.connect.create_temp_file')
    @mock.patch('kfk.commands.connect.open_file_in_system_editor')
    @mock.patch('kfk.commands.connect.click.confirm')
    @mock.patch('kfk.commands.connect.os')
    def test_create_cluster(self, mock_os, mock_click_confirm, mock_open_file_in_system_editor, mock_create_temp_file):
        mock_click_confirm.return_value = True

        result = self.runner.invoke(kfk,
                                    ['connect', '--create', '--cluster', self.cluster, self.connect_config_file,
                                     '-n', self.namespace])
        assert result.exit_code == 0

        with open(r'files/yaml/kafka-connect.yaml') as file:
            expected_connect_yaml = file.read()
            result_connect_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_connect_yaml == result_connect_yaml

    @mock.patch('kfk.commands.connect.create_temp_file')
    @mock.patch('kfk.commands.connect.open_file_in_system_editor')
    @mock.patch('kfk.commands.connect.click.confirm')
    @mock.patch('kfk.commands.connect.os')
    def test_create_cluster_with_yes_flag(self, mock_os, mock_click_confirm, mock_open_file_in_system_editor,
                                          mock_create_temp_file):
        mock_click_confirm.return_value = False

        result = self.runner.invoke(kfk,
                                    ['connect', '--create', '--cluster', self.cluster, self.connect_config_file,
                                     '-n', self.namespace, '-y'])
        assert result.exit_code == 0

        mock_open_file_in_system_editor.assert_not_called()
        with open(r'files/yaml/kafka-connect.yaml') as file:
            expected_connect_yaml = file.read()
            result_connect_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_connect_yaml == result_connect_yaml

    @mock.patch('kfk.commands.connect.create_temp_file')
    @mock.patch('kfk.commands.connect.open_file_in_system_editor')
    @mock.patch('kfk.commands.connect.click.confirm')
    @mock.patch('kfk.commands.connect.os')
    def test_create_cluster_three_replicas(self, mock_os, mock_click_confirm, mock_open_file_in_system_editor,
                                           mock_create_temp_file):
        mock_click_confirm.return_value = True

        result = self.runner.invoke(kfk,
                                    ['connect', '--create', '--cluster', self.cluster, '--replicas', 3,
                                     self.connect_config_file, '-n', self.namespace])
        assert result.exit_code == 0

        with open(r'files/yaml/kafka-connect_with_three_replicas.yaml') as file:
            expected_connect_yaml = file.read()
            result_connect_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_connect_yaml == result_connect_yaml

    @mock.patch('kfk.commands.connect.create_temp_file')
    @mock.patch('kfk.commands.connect.open_file_in_system_editor')
    @mock.patch('kfk.commands.connect.click.confirm')
    @mock.patch('kfk.commands.connect.os')
    def test_create_cluster_with_connector_config(self, mock_os, mock_click_confirm, mock_open_file_in_system_editor,
                                                  mock_create_temp_file):
        mock_click_confirm.return_value = True

        result = self.runner.invoke(kfk,
                                    ['connect', '--create', '--cluster', self.cluster, self.connect_config_file,
                                     self.connector_config_file_1, self.connector_config_file_2, '-n', self.namespace])
        assert result.exit_code == 0

    @mock.patch('kfk.commands.connect.create_temp_file')
    @mock.patch('kfk.commands.connect.open_file_in_system_editor')
    @mock.patch('kfk.commands.connect.click.confirm')
    @mock.patch('kfk.commands.connect.os')
    def test_create_cluster_with_two_connectors_config(self, mock_os, mock_click_confirm,
                                                       mock_open_file_in_system_editor, mock_create_temp_file):
        mock_click_confirm.return_value = True

        result = self.runner.invoke(kfk,
                                    ['connect', '--create', '--cluster', self.cluster, self.connect_config_file,
                                     self.connector_config_file_1, '-n', self.namespace])
        assert result.exit_code == 0
