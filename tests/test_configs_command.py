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

    def test_no_option(self):
        result = self.runner.invoke(kfk, ['configs', '--entity-type', 'topics', '--entity-name', self.topic, '-c',
                                    self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        assert "Missing options: kfk configs" in result.output

    @mock.patch('kfk.topics_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.configs_command.os')
    def test_add_one_topic_config(self, mock_os, mock_resource_exists, mock_get_resource_yaml, mock_create_temp_file):
        mock_resource_exists.return_value = True

        with open(r'files/yaml/topic_without_config.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml

            result = self.runner.invoke(kfk,
                                        ['configs', '--add-config', 'min.insync.replicas=3', '--entity-type', 'topics',
                                         '--entity-name', self.topic, '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'files/yaml/topic_with_one_config.yaml') as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml

    @mock.patch('kfk.topics_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.configs_command.os')
    def test_add_two_topic_configs(self, mock_os, mock_resource_exists, mock_get_resource_yaml, mock_create_temp_file):
        mock_resource_exists.return_value = True

        with open(r'files/yaml/topic_without_config.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml

            result = self.runner.invoke(kfk,
                                        ['configs', '--add-config', 'min.insync.replicas=3', '--add-config',
                                         'cleanup.policy=compact', '--entity-type', 'topics',
                                         '--entity-name', self.topic, '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'files/yaml/topic_with_two_configs.yaml') as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml
