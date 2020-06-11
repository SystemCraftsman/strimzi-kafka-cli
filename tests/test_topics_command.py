from unittest import TestCase, mock
from click.testing import CliRunner
from kfk.topics_command import kfk
from kfk.kubectl_command_builder import Kubectl


class TestKfkTopics(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"
        self.topic = "my-topic"

    def test_no_option(self):
        result = self.runner.invoke(kfk, ['topics', '--topic', self.topic, '-c', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        assert "Missing options: kfk topics" in result.output

    @mock.patch('kfk.topics_command.os')
    def test_list_topics(self, mock_os):
        result = self.runner.invoke(kfk, ['topics', '--list', '-c', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkatopics().label("strimzi.io/cluster={cluster}").namespace(
                self.namespace).build().format(
                cluster=self.cluster))

    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.topics_command.os')
    def test_describe_topic(self, mock_os, mock_resource_exists):
        mock_resource_exists.return_value = True
        result = self.runner.invoke(kfk, ['topics', '--describe', '--topic', self.topic, '-c', self.cluster, '-n',
                                          self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().describe().kafkatopics(self.topic).namespace(self.namespace).build())

    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.topics_command.os')
    def test_describe_topic_output_yaml(self, mock_os, mock_resource_exists):
        mock_resource_exists.return_value = True
        result = self.runner.invoke(kfk, ['topics', '--describe', '--topic', self.topic, '-c', self.cluster, '-n',
                                          self.namespace, '-o', 'yaml'])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkatopics(self.topic).namespace(self.namespace).output("yaml").build())

    @mock.patch('kfk.topics_command.os')
    def test_describe_topic_native(self, mock_os):
        result = self.runner.invoke(kfk, ['topics', '--describe', '--topic', self.topic, '-c', self.cluster, '-n',
                                          self.namespace, '--native'])
        assert result.exit_code == 0
        native_command = "bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic {topic}"
        mock_os.system.assert_called_with(
            Kubectl().exec("-it", "{cluster}-kafka-0").container("kafka").namespace(self.namespace).exec_command(
                native_command).build().format(topic=self.topic, cluster=self.cluster))

    def test_create_topic_without_required_params(self):
        result = self.runner.invoke(kfk,
                                    ['topics', '--create', '--topic', self.topic, '-c',
                                     self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 2

    @mock.patch('kfk.topics_command.os')
    def test_create_topic(self, mock_os):
        result = self.runner.invoke(kfk,
                                    ['topics', '--create', '--topic', self.topic, '--partitions', '12',
                                     '--replication-factor', '3', '-c',
                                     self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 0
        with open(r'yaml/topic_create.yaml') as file:
            topic_yaml = file.read()
            mock_os.system.assert_called_with(
                'echo "{topic_yaml}" | '.format(topic_yaml=topic_yaml) + Kubectl().create().from_file("-").namespace(
                    self.namespace).build())

    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.topics_command.os')
    def test_delete_topic(self, mock_os, mock_resource_exists):
        mock_resource_exists.return_value = True
        result = self.runner.invoke(kfk,
                                    ['topics', '--delete', '--topic', self.topic, '-c', self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().delete().kafkatopics(self.topic).namespace(self.namespace).build())

    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.topics_command.os')
    def test_alter_topic_with_no_params(self, mock_os, mock_resource_exists, mock_get_resource_yaml):
        mock_resource_exists.return_value = True
        with open(r'yaml/topic_create.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk,
                                        ['topics', '--alter', '--topic', self.topic, '-c', self.cluster, '-n',
                                         self.namespace])
            assert result.exit_code == 0
            mock_os.system.assert_called_with(
                'echo "{topic_yaml}" | '.format(topic_yaml=topic_yaml) + Kubectl().apply().from_file("-").namespace(
                    self.namespace).build())

    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.topics_command.os')
    def test_alter_topic_without_config(self, mock_os, mock_resource_exists, mock_get_resource_yaml):
        mock_resource_exists.return_value = True
        with open(r'yaml/topic_create.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk,
                                        ['topics', '--alter', '--topic', self.topic, '--partitions', '24',
                                         '--replication-factor', '3', '-c', self.cluster, '-n', self.namespace])
            assert result.exit_code == 0
            with open(r'yaml/topic_alter_without_config.yaml') as file:
                topic_yaml = file.read()
                mock_os.system.assert_called_with(
                    'echo "{topic_yaml}" | '.format(topic_yaml=topic_yaml) + Kubectl().apply().from_file("-").namespace(
                        self.namespace).build())

    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.topics_command.os')
    def test_alter_topic_with_config(self, mock_os, mock_resource_exists, mock_get_resource_yaml):
        mock_resource_exists.return_value = True
        with open(r'yaml/topic_create.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk,
                                        ['topics', '--alter', '--topic', self.topic, '--partitions', '24',
                                         '--replication-factor', '3', '--config', 'min.insync.replicas=3', '-c',
                                         self.cluster, '-n',
                                         self.namespace])
            assert result.exit_code == 0
            with open(r'yaml/topic_alter_with_one_config.yaml') as file:
                topic_yaml = file.read()
                mock_os.system.assert_called_with(
                    'echo "{topic_yaml}" | '.format(topic_yaml=topic_yaml) + Kubectl().apply().from_file("-").namespace(
                        self.namespace).build())

    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.topics_command.os')
    def test_alter_topic_with_two_configs(self, mock_os, mock_resource_exists, mock_get_resource_yaml):
        mock_resource_exists.return_value = True
        with open(r'yaml/topic_create.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk,
                                        ['topics', '--alter', '--topic', self.topic, '--partitions', '24',
                                         '--replication-factor', '3', '--config', 'min.insync.replicas=3', '--config',
                                         'cleanup.policy=compact', '-c', self.cluster, '-n',
                                         self.namespace])
            assert result.exit_code == 0
            with open(r'yaml/topic_alter_with_two_configs.yaml') as file:
                topic_yaml = file.read()
                mock_os.system.assert_called_with(
                    'echo "{topic_yaml}" | '.format(topic_yaml=topic_yaml) + Kubectl().apply().from_file("-").namespace(
                        self.namespace).build())

    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.topics_command.os')
    def test_alter_topic_with_two_configs_delete_one_config(self, mock_os, mock_resource_exists,
                                                            mock_get_resource_yaml):
        mock_resource_exists.return_value = True
        with open(r'yaml/topic_alter_with_two_configs.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk,
                                        ['topics', '--alter', '--topic', self.topic, '--delete-config',
                                         'cleanup.policy', '-c', self.cluster, '-n',
                                         self.namespace])
            assert result.exit_code == 0
            with open(r'yaml/topic_alter_with_one_config.yaml') as file:
                topic_yaml = file.read()
                mock_os.system.assert_called_with(
                    'echo "{topic_yaml}" | '.format(topic_yaml=topic_yaml) + Kubectl().apply().from_file("-").namespace(
                        self.namespace).build())

    @mock.patch('kfk.commons.get_resource_yaml')
    @mock.patch('kfk.topics_command.resource_exists')
    @mock.patch('kfk.topics_command.os')
    def test_alter_topic_with_two_configs_delete_two_configs(self, mock_os, mock_resource_exists,
                                                             mock_get_resource_yaml):
        mock_resource_exists.return_value = True
        with open(r'yaml/topic_alter_with_two_configs.yaml') as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml
            result = self.runner.invoke(kfk,
                                        ['topics', '--alter', '--topic', self.topic, '--delete-config',
                                         'cleanup.policy', '--delete-config',
                                         'min.insync.replicas', '-c', self.cluster, '-n',
                                         self.namespace])
            assert result.exit_code == 0
            with open(r'yaml/topic_alter_without_config.yaml') as file:
                topic_yaml = file.read()
                mock_os.system.assert_called_with(
                    'echo "{topic_yaml}" | '.format(topic_yaml=topic_yaml) + Kubectl().apply().from_file("-").namespace(
                        self.namespace).build())
