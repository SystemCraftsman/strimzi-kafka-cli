from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.commands.operator import kfk


class TestKfkOperator(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"
        self.installation_file_count = 28

    @mock.patch("kfk.commands.operator.create_using_yaml")
    def test_install_strimzi(self, mock_create_using_yaml):
        result = self.runner.invoke(
            kfk, ["operator", "--install", "-n", self.namespace]
        )
        assert result.exit_code == 0
        assert mock_create_using_yaml.call_count == self.installation_file_count

    @mock.patch("kfk.commands.operator.delete_using_yaml")
    def test_uninstall_strimzi(self, mock_delete_using_yaml):
        result = self.runner.invoke(
            kfk, ["operator", "--uninstall", "-n", self.namespace]
        )
        assert result.exit_code == 0
        assert mock_delete_using_yaml.call_count == self.installation_file_count
