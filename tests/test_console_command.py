from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.commands.console import kfk


class TestKfkConsole(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"
        self.topic = "my-topic"

    @mock.patch("kfk.commands.console.exec_on_pod_interactive")
    def test_console_consumer(self, mock_exec_on_pod_interactive):
        result = self.runner.invoke(
            kfk,
            [
                "console-consumer",
                "--topic",
                self.topic,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        mock_exec_on_pod_interactive.assert_called_with(
            self.cluster + "-broker-0",
            "kafka",
            self.namespace,
            (
                "bin/kafka-console-consumer.sh --bootstrap-server"
                f" {self.cluster}-kafka-brokers:9092"
                f" --topic {self.topic} "
            ),
        )

    @mock.patch("kfk.commons.transfer_file_to_container")
    @mock.patch("kfk.commands.console.exec_on_pod_interactive")
    def test_console_consumer_with_consumer_config(
        self, mock_exec_on_pod_interactive, mock_transfer_file_to_container
    ):
        result = self.runner.invoke(
            kfk,
            [
                "console-consumer",
                "--topic",
                self.topic,
                "--consumer.config",
                "tests/files/client.properties",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        mock_exec_on_pod_interactive.assert_called_with(
            self.cluster + "-broker-0",
            "kafka",
            self.namespace,
            (
                "bin/kafka-console-consumer.sh --bootstrap-server"
                f" {self.cluster}-kafka-brokers:9093"
                f" --topic {self.topic} "
                " --consumer.config /tmp/client.properties;rm -rf"
                " /tmp/truststore.jks;rm -rf /tmp/user.p12;rm -rf"
                " /tmp/client.properties;"
            ),
        )

    @mock.patch("kfk.commands.console.exec_on_pod_interactive")
    def test_console_consumer_with_from_beginning(self, mock_exec_on_pod_interactive):
        result = self.runner.invoke(
            kfk,
            [
                "console-consumer",
                "--topic",
                self.topic,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
                "--from-beginning",
            ],
        )
        assert result.exit_code == 0

        mock_exec_on_pod_interactive.assert_called_with(
            self.cluster + "-broker-0",
            "kafka",
            self.namespace,
            (
                "bin/kafka-console-consumer.sh --bootstrap-server"
                f" {self.cluster}-kafka-brokers:9092"
                f" --topic {self.topic} --from-beginning"
            ),
        )

    @mock.patch("kfk.commands.console.exec_on_pod_interactive")
    def test_console_producer(self, mock_exec_on_pod_interactive):
        result = self.runner.invoke(
            kfk,
            [
                "console-producer",
                "--topic",
                self.topic,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_exec_on_pod_interactive.assert_called_with(
            self.cluster + "-broker-0",
            "kafka",
            self.namespace,
            (
                "bin/kafka-console-producer.sh --bootstrap-server"
                f" {self.cluster}-kafka-brokers:9092"
                f" --topic {self.topic}"
            ),
        )

    @mock.patch("kfk.commons.transfer_file_to_container")
    @mock.patch("kfk.commands.console.exec_on_pod_interactive")
    def test_console_producer_with_producer_config(
        self, mock_exec_on_pod_interactive, mock_transfer_file_to_container
    ):
        result = self.runner.invoke(
            kfk,
            [
                "console-producer",
                "--topic",
                self.topic,
                "--producer.config",
                "tests/files/client.properties",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_exec_on_pod_interactive.assert_called_with(
            self.cluster + "-broker-0",
            "kafka",
            self.namespace,
            (
                "bin/kafka-console-producer.sh --bootstrap-server"
                f" {self.cluster}-kafka-brokers:9093"
                f" --topic {self.topic}"
                " --producer.config /tmp/client.properties;rm -rf"
                " /tmp/truststore.jks;rm -rf /tmp/user.p12;rm -rf"
                " /tmp/client.properties;"
            ),
        )
