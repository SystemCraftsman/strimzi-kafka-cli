from unittest import TestCase, mock
from click.testing import CliRunner
from kfk.clusters_command import kfk
from kfk.kubectl_command_builder import Kubectl


class TestKfkClusters(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"

    def test_no_option(self):
        result = self.runner.invoke(kfk, ['clusters', '--cluster', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        assert "Missing options: kfk clusters" in result.output

    @mock.patch('kfk.clusters_command.os')
    def test_list_clusters(self, mock_os):
        result = self.runner.invoke(kfk, ['clusters', '--list', '-n', self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().get().kafkas().namespace(self.namespace).build())

    @mock.patch('kfk.clusters_command.os')
    def test_list_clusters_all_namespaces(self, mock_os):
        result = self.runner.invoke(kfk, ['clusters', '--list'])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().get().kafkas().namespace().build())

    @mock.patch('kfk.clusters_command.os')
    def test_describe_cluster(self, mock_os):
        result = self.runner.invoke(kfk, ['clusters', '--describe', '--cluster', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().describe().kafkas(self.cluster).namespace(self.namespace).build())

    @mock.patch('kfk.clusters_command.os')
    def test_describe_cluster_output_yaml(self, mock_os):
        result = self.runner.invoke(kfk,
                                    ['clusters', '--describe', '--cluster', self.cluster, '-n', self.namespace, '-o',
                                     'yaml'])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkas(self.cluster).namespace(self.namespace).output("yaml").build())

    @mock.patch('kfk.clusters_command.os')
    def test_alter_cluster_without_config(self, mock_os):
        result = self.runner.invoke(kfk, ['clusters', '--alter', '--cluster', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().edit().kafkas(self.cluster).namespace(self.namespace).build())

    @mock.patch('kfk.clusters_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.clusters_command.resource_exists')
    @mock.patch('kfk.clusters_command.os')
    def test_alter_cluster_with_one_additional_config(self, mock_os, mock_resource_exists, mock_get_resource_yaml,
                                                      mock_create_temp_file):
        mock_resource_exists.return_value = True
        with open(r'files/yaml/kafka-ephemeral.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk, ['clusters', '--alter', '--config', 'unclean.leader.election.enable=true',
                                              '--cluster', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'files/yaml/kafka-ephemeral_with_one_additional_config.yaml') as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml

    @mock.patch('kfk.clusters_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.clusters_command.resource_exists')
    @mock.patch('kfk.clusters_command.os')
    def test_alter_cluster_with_two_additional_configs(self, mock_os, mock_resource_exists, mock_get_resource_yaml,
                                                       mock_create_temp_file):
        mock_resource_exists.return_value = True
        with open(r'files/yaml/kafka-ephemeral.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk, ['clusters', '--alter', '--config', 'unclean.leader.election.enable=true',
                                              '--config', 'log.retention.hours=168',
                                              '--cluster', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'files/yaml/kafka-ephemeral_with_two_additional_configs.yaml') as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml

    @mock.patch('kfk.clusters_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.clusters_command.resource_exists')
    @mock.patch('kfk.clusters_command.os')
    def test_alter_cluster_with_two_additional_configs_delete_one_config(self, mock_os, mock_resource_exists,
                                                                         mock_get_resource_yaml, mock_create_temp_file):
        mock_resource_exists.return_value = True
        with open(r'files/yaml/kafka-ephemeral_with_two_additional_configs.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk, ['clusters', '--alter', '--delete-config', 'log.retention.hours',
                                              '--cluster', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'files/yaml/kafka-ephemeral_with_one_additional_config.yaml') as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml

    @mock.patch('kfk.clusters_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.clusters_command.resource_exists')
    @mock.patch('kfk.clusters_command.os')
    def test_alter_cluster_with_two_additional_configs_delete_two_configs(self, mock_os, mock_resource_exists,
                                                                          mock_get_resource_yaml,
                                                                          mock_create_temp_file):
        mock_resource_exists.return_value = True
        with open(r'files/yaml/kafka-ephemeral_with_two_additional_configs.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk, ['clusters', '--alter', '--delete-config', 'log.retention.hours',
                                              '--delete-config', 'unclean.leader.election.enable', '--cluster',
                                              self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'files/yaml/kafka-ephemeral_two_additional_configs_deleted.yaml') as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml

    @mock.patch('kfk.clusters_command.click.confirm')
    @mock.patch('kfk.clusters_command.os')
    def test_delete_cluster(self, mock_os, mock_click_confirm):
        mock_click_confirm.return_value = True
        result = self.runner.invoke(kfk, ['clusters', '--delete', '--cluster', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().delete().kafkas(self.cluster).namespace(self.namespace).build())

    @mock.patch('kfk.clusters_command.create_temp_file')
    @mock.patch('kfk.clusters_command.open_file_in_system_editor')
    @mock.patch('kfk.clusters_command.click.confirm')
    @mock.patch('kfk.clusters_command.os')
    def test_create_cluster(self, mock_os, mock_click_confirm, mock_open_file_in_system_editor, mock_create_temp_file):
        mock_click_confirm.return_value = True

        new_cluster_name = "my-cluster-with-new-name"

        result = self.runner.invoke(kfk, ['clusters', '--create', '--cluster', new_cluster_name, '-n', self.namespace])
        assert result.exit_code == 0

        with open(r'files/yaml/kafka-ephemeral_name_updated.yaml') as file:
            expected_kafka_yaml = file.read()
            result_kafka_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_kafka_yaml == result_kafka_yaml
