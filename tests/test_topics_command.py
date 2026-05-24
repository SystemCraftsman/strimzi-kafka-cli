from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.commands.topics import kfk

STRIMZI_PATH = "tests/files/strimzi"


@mock.patch("kfk.commands.topics.STRIMZI_PATH", STRIMZI_PATH)
class TestKfkTopics(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"
        self.topic = "my-topic"

    def test_no_option(self):
        result = self.runner.invoke(
            kfk,
            ["topics", "--topic", self.topic, "-c", self.cluster, "-n", self.namespace],
        )
        assert result.exit_code == 1
        assert "Missing options: kfk topics" in result.output

    @mock.patch("kfk.commands.topics.list_resource")
    def test_list_topics(self, mock_list_resource):
        result = self.runner.invoke(
            kfk, ["topics", "--list", "-c", self.cluster, "-n", self.namespace]
        )
        assert result.exit_code == 0
        mock_list_resource.assert_called_with(
            "kafkatopics",
            self.namespace,
            label=f"strimzi.io/cluster={self.cluster}",
        )

    @mock.patch("kfk.commands.topics.describe_resource")
    def test_describe_topic(self, mock_describe_resource):
        result = self.runner.invoke(
            kfk,
            [
                "topics",
                "--describe",
                "--topic",
                self.topic,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_describe_resource.assert_called_with(
            "kafkatopics", self.topic, self.namespace
        )

    @mock.patch("kfk.commands.topics.get_resource")
    def test_describe_topic_output_yaml(self, mock_get_resource):
        mock_get_resource.return_value = {"metadata": {"name": self.topic}}
        result = self.runner.invoke(
            kfk,
            [
                "topics",
                "--describe",
                "--topic",
                self.topic,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
                "-o",
                "yaml",
            ],
        )
        assert result.exit_code == 0
        mock_get_resource.assert_called_with("kafkatopics", self.topic, self.namespace)

    @mock.patch("kfk.commands.topics.exec_on_pod")
    def test_describe_topic_native(self, mock_exec_on_pod):
        result = self.runner.invoke(
            kfk,
            [
                "topics",
                "--describe",
                "--topic",
                self.topic,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
                "--native",
            ],
        )
        assert result.exit_code == 0
        mock_exec_on_pod.assert_called_with(
            self.cluster + "-broker-0",
            "kafka",
            self.namespace,
            (
                "bin/kafka-topics.sh --bootstrap-server"
                f" {self.cluster}-kafka-brokers:9092"
                f" --describe --topic {self.topic}"
            ),
        )

    @mock.patch("kfk.commons.transfer_file_to_container")
    @mock.patch("kfk.commands.topics.exec_on_pod")
    def test_describe_topic_native_with_command_config(
        self, mock_exec_on_pod, mock_transfer_file_to_container
    ):
        result = self.runner.invoke(
            kfk,
            [
                "topics",
                "--describe",
                "--topic",
                self.topic,
                "--command-config",
                "tests/files/client.properties",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
                "--native",
            ],
        )
        assert result.exit_code == 0
        mock_exec_on_pod.assert_called_with(
            self.cluster + "-broker-0",
            "kafka",
            self.namespace,
            (
                "bin/kafka-topics.sh --bootstrap-server"
                f" {self.cluster}-kafka-brokers:9093"
                f" --describe --topic {self.topic}"
                " --command-config /tmp/client.properties;rm -rf"
                " /tmp/truststore.jks;rm -rf /tmp/user.p12;rm -rf"
                " /tmp/client.properties;"
            ),
        )

    @mock.patch("kfk.commands.topics.create_temp_file")
    @mock.patch("kfk.commands.topics.create_using_yaml")
    def test_create_topic(self, mock_create_using_yaml, mock_create_temp_file):
        result = self.runner.invoke(
            kfk,
            [
                "topics",
                "--create",
                "--topic",
                self.topic,
                "--partitions",
                "12",
                "--replication-factor",
                "3",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )

        assert result.exit_code == 0

        with open("tests/files/yaml/topic.yaml") as file:
            expected_topic_yaml = file.read()
            result_topic_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_topic_yaml == result_topic_yaml

        mock_create_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.topics.create_temp_file")
    @mock.patch("kfk.commands.topics.create_using_yaml")
    def test_create_topic_with_config(
        self, mock_create_using_yaml, mock_create_temp_file
    ):
        result = self.runner.invoke(
            kfk,
            [
                "topics",
                "--create",
                "--topic",
                self.topic,
                "--partitions",
                "24",
                "--replication-factor",
                "3",
                "--config",
                "min.insync.replicas=3",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )

        assert result.exit_code == 0

        with open("tests/files/yaml/topic_with_one_config.yaml") as file:
            expected_topic_yaml = file.read()
            result_topic_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_topic_yaml == result_topic_yaml

        mock_create_using_yaml.assert_called_once()

    def test_create_topic_without_required_params(self):
        result = self.runner.invoke(
            kfk,
            [
                "topics",
                "--create",
                "--topic",
                self.topic,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 2

    @mock.patch("kfk.commands.topics.delete_using_yaml")
    def test_delete_topic(self, mock_delete_using_yaml):
        result = self.runner.invoke(
            kfk,
            [
                "topics",
                "--delete",
                "--topic",
                self.topic,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )

        assert result.exit_code == 0

        mock_delete_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.topics.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.topics.replace_using_yaml")
    def test_alter_topic_with_no_params(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/topic.yaml") as file:
            expected_topic_yaml = file.read()
            mock_get_resource_yaml.return_value = expected_topic_yaml

            result = self.runner.invoke(
                kfk,
                [
                    "topics",
                    "--alter",
                    "--topic",
                    self.topic,
                    "-c",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )

            assert result.exit_code == 0

            result_topic_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_topic_yaml == result_topic_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.topics.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.topics.replace_using_yaml")
    def test_alter_topic_without_config(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/topic.yaml") as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml

            result = self.runner.invoke(
                kfk,
                [
                    "topics",
                    "--alter",
                    "--topic",
                    self.topic,
                    "--partitions",
                    "24",
                    "--replication-factor",
                    "3",
                    "-c",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )

            assert result.exit_code == 0

            with open("tests/files/yaml/topic_without_config.yaml") as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.topics.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.topics.replace_using_yaml")
    def test_alter_topic_with_config(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/topic.yaml") as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml

            result = self.runner.invoke(
                kfk,
                [
                    "topics",
                    "--alter",
                    "--topic",
                    self.topic,
                    "--partitions",
                    "24",
                    "--replication-factor",
                    "3",
                    "--config",
                    "min.insync.replicas=3",
                    "-c",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )

            assert result.exit_code == 0

            with open("tests/files/yaml/topic_with_one_config.yaml") as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.topics.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.topics.replace_using_yaml")
    def test_alter_topic_with_two_configs(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/topic.yaml") as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml

            result = self.runner.invoke(
                kfk,
                [
                    "topics",
                    "--alter",
                    "--topic",
                    self.topic,
                    "--partitions",
                    "24",
                    "--replication-factor",
                    "3",
                    "--config",
                    "min.insync.replicas=3",
                    "--config",
                    "cleanup.policy=compact",
                    "-c",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )

            assert result.exit_code == 0

            with open("tests/files/yaml/topic_with_two_configs.yaml") as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.topics.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.topics.replace_using_yaml")
    def test_alter_topic_with_two_configs_delete_one_config(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/topic_with_two_configs.yaml") as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml

            result = self.runner.invoke(
                kfk,
                [
                    "topics",
                    "--alter",
                    "--topic",
                    self.topic,
                    "--delete-config",
                    "cleanup.policy",
                    "-c",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )

            assert result.exit_code == 0

            with open("tests/files/yaml/topic_with_one_config.yaml") as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.topics.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.topics.replace_using_yaml")
    def test_alter_topic_with_two_configs_delete_two_configs(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/topic_with_two_configs.yaml") as file:
            topic_yaml = file.read()
            mock_get_resource_yaml.return_value = topic_yaml

            result = self.runner.invoke(
                kfk,
                [
                    "topics",
                    "--alter",
                    "--topic",
                    self.topic,
                    "--delete-config",
                    "cleanup.policy",
                    "--delete-config",
                    "min.insync.replicas",
                    "-c",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )

            assert result.exit_code == 0

            with open("tests/files/yaml/topic_without_config.yaml") as file:
                expected_topic_yaml = file.read()
                result_topic_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_topic_yaml == result_topic_yaml

        mock_replace_using_yaml.assert_called_once()
