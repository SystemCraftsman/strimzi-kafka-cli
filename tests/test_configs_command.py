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
        self.user = "my-user"

    def test_no_option(self):
        result = self.runner.invoke(kfk, ['configs', '--entity-type', 'topics', '--entity-name', self.topic, '-c',
                                          self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        assert "Missing options: kfk configs" in result.output

    def test_wrong_entity_type(self):
        result = self.runner.invoke(kfk, ['configs', '--entity-type', 'foos', '--entity-name', self.topic, '-c',
                                          self.cluster, '-n', self.namespace])
        assert result.exit_code == 2

    @mock.patch('kfk.topics_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.topics_command.os')
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
    @mock.patch('kfk.topics_command.os')
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

    @mock.patch('kfk.topics_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.topics_command.os')
    def test_delete_one_topic_config(self, mock_os, mock_resource_exists, mock_get_resource_yaml,
                                     mock_create_temp_file):
        mock_resource_exists.return_value = True

        with open(r'files/yaml/topic_with_two_configs.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml

            result = self.runner.invoke(kfk,
                                        ['configs', '--delete-config', 'cleanup.policy', '--entity-type', 'topics',
                                         '--entity-name', self.topic, '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'files/yaml/topic_with_one_config.yaml') as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml

    @mock.patch('kfk.configs_command.os')
    def test_describe_topic_config_native(self, mock_os):
        result = self.runner.invoke(kfk,
                                    ['configs', '--describe', '--entity-type', 'topics',
                                     '--entity-name', self.topic, '--native', '-c', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0

        native_command = "bin/kafka-configs.sh --bootstrap-server {cluster}-kafka-brokers:9092 --entity-type " \
                         "topics --entity-name {entity_name} --describe"
        mock_os.system.assert_called_with(
            Kubectl().exec("-it", "{cluster}-kafka-0").container("kafka").namespace(self.namespace).exec_command(
                native_command).build().format(cluster=self.cluster, entity_name=self.topic))

    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.topics_command.os')
    def test_describe_topic_config(self, mock_os, mock_resource_exists):
        mock_resource_exists.return_value = True
        result = self.runner.invoke(kfk,
                                    ['configs', '--describe', '--entity-type', 'topics',
                                     '--entity-name', self.topic, '-c', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().describe().kafkatopics(self.topic).namespace(self.namespace).build())

    @mock.patch('kfk.users_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_add_one_user_config(self, mock_os, mock_resource_exists, mock_get_resource_yaml, mock_create_temp_file):
        mock_resource_exists.return_value = True

        with open(r'files/yaml/user_with_authentication_scram.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(kfk,
                                        ['configs', '--add-config', 'request_percentage=55', '--entity-type', 'users',
                                         '--entity-name', self.user, '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'files/yaml/user_with_one_quota.yaml') as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_user_yaml == result_user_yaml

    @mock.patch('kfk.users_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_add_two_user_configs(self, mock_os, mock_resource_exists, mock_get_resource_yaml, mock_create_temp_file):
        mock_resource_exists.return_value = True

        with open(r'files/yaml/user_with_authentication_scram.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(kfk,
                                        ['configs', '--add-config', 'request_percentage=55', '--add-config',
                                         'consumer_byte_rate=2097152', '--entity-type', 'users',
                                         '--entity-name', self.user, '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'files/yaml/user_with_two_quotas.yaml') as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_user_yaml == result_user_yaml

    @mock.patch('kfk.users_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.users_command.resource_exists')
    @mock.patch('kfk.users_command.os')
    def test_delete_one_user_config(self, mock_os, mock_resource_exists, mock_get_resource_yaml, mock_create_temp_file):
        mock_resource_exists.return_value = True

        with open(r'files/yaml/user_with_two_quotas.yaml') as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(kfk,
                                        ['configs', '--delete-config', 'consumer_byte_rate', '--entity-type', 'users',
                                         '--entity-name', self.user, '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'files/yaml/user_with_one_quota.yaml') as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_user_yaml == result_user_yaml

    @mock.patch('kfk.clusters_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.clusters_command.resource_exists')
    @mock.patch('kfk.clusters_command.os')
    def test_add_one_broker_config_with_wrong_entity_name(self, mock_os, mock_resource_exists, mock_get_resource_yaml, mock_create_temp_file):
        mock_resource_exists.return_value = True
        with open(r'files/yaml/kafka-ephemeral.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk,
                                        ['configs', '--add-config', 'unclean.leader.election.enable=true',
                                         '--entity-type', 'brokers', '--entity-name', 'another_name', '-c', self.cluster,
                                         '-n', self.namespace])
            assert result.exit_code == 0
            assert "`entity-name` for brokers should be set as `all`" in result.output

    @mock.patch('kfk.clusters_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.clusters_command.resource_exists')
    @mock.patch('kfk.clusters_command.os')
    def test_add_one_broker_config(self, mock_os, mock_resource_exists, mock_get_resource_yaml, mock_create_temp_file):
        mock_resource_exists.return_value = True
        with open(r'files/yaml/kafka-ephemeral.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk,
                                        ['configs', '--add-config', 'unclean.leader.election.enable=true',
                                         '--entity-type', 'brokers', '--entity-name', 'all', '-c', self.cluster,
                                         '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'files/yaml/kafka-ephemeral_with_one_additional_config.yaml') as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml

    @mock.patch('kfk.clusters_command.create_temp_file')
    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.clusters_command.resource_exists')
    @mock.patch('kfk.clusters_command.os')
    def test_delete_one_broker_config(self, mock_os, mock_resource_exists, mock_get_resource_yaml, mock_create_temp_file):
        mock_resource_exists.return_value = True
        with open(r'files/yaml/kafka-ephemeral_with_one_additional_config.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk,
                                        ['configs', '--delete-config', 'unclean.leader.election.enable',
                                         '--entity-type', 'brokers', '--entity-name', 'all', '-c', self.cluster,
                                         '-n', self.namespace])
            assert result.exit_code == 0

            with open(r'files/yaml/kafka-ephemeral_two_additional_configs_deleted.yaml') as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml
