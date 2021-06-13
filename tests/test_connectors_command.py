from unittest import TestCase, mock

import click
import yaml

from click.testing import CliRunner
from kfk.commands.connectors import kfk
from kfk.kubectl_command_builder import Kubectl


class TestKfkConnectors(TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-connect-cluster"
        self.namespace = "kafka"
        self.connector_config_file = "files/twitter_connector.properties"
        self.connector = "twitter-source-connector"

    def test_no_option(self):
        result = self.runner.invoke(kfk,
                                    ['connectors', self.connector_config_file, '-c', self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 0
        assert "Missing options: kfk connectors" in result.output

    @mock.patch('kfk.commands.connectors.os')
    def test_list_connectors(self, mock_os):
        result = self.runner.invoke(kfk, ['connectors', '--list', '-c', self.cluster, '-n', self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkaconnectors().label("strimzi.io/cluster={cluster}").namespace(
                self.namespace).build().format(
                cluster=self.cluster))

    @mock.patch('kfk.commands.connectors.os')
    def test_describe_connector(self, mock_os):
        result = self.runner.invoke(kfk,
                                    ['connectors', '--describe', '--connector', self.connector, '-c', self.cluster,
                                     '-n', self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().describe().kafkaconnectors(self.connector).namespace(self.namespace).build())

    @mock.patch('kfk.commands.connectors.os')
    def test_describe_connector_output_yaml(self, mock_os):
        result = self.runner.invoke(kfk, ['connectors', '--describe', '--connector', self.connector, '-c', self.cluster,
                                          '-n', self.namespace, '-o', 'yaml'])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkaconnectors(self.connector).namespace(self.namespace).output("yaml").build())

    @mock.patch('kfk.commands.connectors.os')
    def test_delete_connector(self, mock_os):
        result = self.runner.invoke(kfk,
                                    ['connectors', '--delete', '--connector', self.connector, '-c', self.cluster, '-n',
                                     self.namespace])

        assert result.exit_code == 0

        mock_os.system.assert_called_with(
            Kubectl().delete().kafkaconnectors(self.connector).namespace(self.namespace).build())
