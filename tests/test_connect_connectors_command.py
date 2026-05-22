from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.commands.connect.connectors import connect

STRIMZI_PATH = "tests/files/strimzi"


@mock.patch("kfk.commands.connect.connectors.STRIMZI_PATH", STRIMZI_PATH)
class TestKfkConnectors(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-connect-cluster"
        self.namespace = "kafka"
        self.connector_config_file = "tests/files/twitter-connector.properties"
        self.connector = "twitter-source-connector"

    def test_no_option(self):
        result = self.runner.invoke(
            connect,
            [
                "connectors",
                self.connector_config_file,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 1
        assert "Missing options: kfk connectors" in result.output

    @mock.patch("kfk.commands.connect.connectors.list_resource")
    def test_list_connectors(self, mock_list_resource):
        result = self.runner.invoke(
            connect, ["connectors", "--list", "-c", self.cluster, "-n", self.namespace]
        )
        assert result.exit_code == 0
        mock_list_resource.assert_called_with(
            "kafkaconnectors",
            self.namespace,
            label=f"strimzi.io/cluster={self.cluster}",
        )

    @mock.patch("kfk.commands.connect.connectors.describe_resource")
    def test_describe_connector(self, mock_describe_resource):
        result = self.runner.invoke(
            connect,
            [
                "connectors",
                "--describe",
                "--connector",
                self.connector,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_describe_resource.assert_called_with(
            "kafkaconnectors", self.connector, self.namespace
        )

    @mock.patch("kfk.commands.connect.connectors.get_resource")
    def test_describe_connector_output_yaml(self, mock_get_resource):
        mock_get_resource.return_value = {"metadata": {"name": self.connector}}
        result = self.runner.invoke(
            connect,
            [
                "connectors",
                "--describe",
                "--connector",
                self.connector,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
                "-o",
                "yaml",
            ],
        )
        assert result.exit_code == 0
        mock_get_resource.assert_called_with(
            "kafkaconnectors", self.connector, self.namespace
        )

    @mock.patch("kfk.commands.connect.connectors.delete_using_yaml")
    def test_delete_connector(self, mock_delete_using_yaml):
        result = self.runner.invoke(
            connect,
            [
                "connectors",
                "--delete",
                "--connector",
                self.connector,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )

        assert result.exit_code == 0

        mock_delete_using_yaml.assert_called_once()

    def test_create_connector_without_config_file(self):
        result = self.runner.invoke(
            connect,
            ["connectors", "--create", "-c", self.cluster, "-n", self.namespace],
        )

        assert result.exit_code == 2

    @mock.patch("kfk.commands.connect.connectors.create_temp_file")
    @mock.patch("kfk.commands.connect.connectors.create_using_yaml")
    def test_create_connector(self, mock_create_using_yaml, mock_create_temp_file):
        result = self.runner.invoke(
            connect,
            [
                "connectors",
                "--create",
                self.connector_config_file,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )

        assert result.exit_code == 0

        with open("tests/files/yaml/kafka-connect-connector-twitter.yaml") as file:
            expected_connector_yaml = file.read()
            result_connector_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_connector_yaml == result_connector_yaml

        mock_create_using_yaml.assert_called_once()

    def test_alter_connector_without_config_file(self):
        result = self.runner.invoke(
            connect, ["connectors", "--alter", "-c", self.cluster, "-n", self.namespace]
        )

        assert result.exit_code == 2

    @mock.patch("kfk.commands.connect.connectors.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.connect.connectors.replace_using_yaml")
    def test_alter_connector(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/kafka-connect-connector-twitter.yaml") as file:
            connector_yaml = file.read()
            mock_get_resource_yaml.return_value = connector_yaml

            result = self.runner.invoke(
                connect,
                [
                    "connectors",
                    "--alter",
                    "tests/files/twitter_connector_with_config_change.properties",
                    "-c",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )

            assert result.exit_code == 0

            with open(
                "tests/files/yaml/kafka-connect-connector-"
                "twitter_with_config_change.yaml"
            ) as file:
                expected_connector_yaml = file.read()
                result_connector_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_connector_yaml == result_connector_yaml

        mock_replace_using_yaml.assert_called_once()
