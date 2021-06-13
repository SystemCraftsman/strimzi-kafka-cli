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

    def test_no_option(self):
        result = self.runner.invoke(kfk,
                                    ['connectors', self.connector_config_file, '-c', self.cluster, '-n',
                                     self.namespace])
        assert result.exit_code == 0
        assert "Missing options: kfk connectors" in result.output

