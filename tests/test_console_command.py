from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.commands.console import kfk
from kfk.kubectl_command_builder import Kubectl


class TestKfkConsole(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"
        self.topic = "my-topic"

    @mock.patch("kfk.commands.console.os")
    def test_console_consumer(self, mock_os):
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

        native_command = (
            "bin/kafka-console-consumer.sh --bootstrap-server"
            " my-cluster-kafka-brokers:9092 --topic {topic} "
        )
        mock_os.system.assert_called_with(
            Kubectl()
            .exec("-it", "{cluster}-kafka-0")
            .container("kafka")
            .namespace(self.namespace)
            .exec_command(native_command)
            .build()
            .format(cluster=self.cluster, topic=self.topic)
        )

    @mock.patch("kfk.commons.transfer_file_to_container")
    @mock.patch("kfk.commands.console.os")
    def test_console_consumer_with_consumer_config(
        self, mock_os, mock_transfer_file_to_container
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

        native_command = (
            "bin/kafka-console-consumer.sh --bootstrap-server"
            " {cluster}-kafka-brokers:9093 --topic {topic}  --consumer.config"
            " /tmp/client.properties;rm -rf /tmp/truststore.jks;rm -rf /tmp/user.p12;rm"
            " -rf /tmp/client.properties;"
        )
        mock_os.system.assert_called_with(
            Kubectl()
            .exec("-it", "{cluster}-kafka-0")
            .container("kafka")
            .namespace(self.namespace)
            .exec_command(native_command)
            .build()
            .format(cluster=self.cluster, topic=self.topic)
        )

    @mock.patch("kfk.commands.console.os")
    def test_console_consumer_with_from_beginning(self, mock_os):
        from_beginning = True
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

        native_command = (
            "bin/kafka-console-consumer.sh --bootstrap-server"
            " my-cluster-kafka-brokers:9092 --topic {topic} {from_beginning}"
        )
        mock_os.system.assert_called_with(
            Kubectl()
            .exec("-it", "{cluster}-kafka-0")
            .container("kafka")
            .namespace(self.namespace)
            .exec_command(native_command)
            .build()
            .format(
                cluster=self.cluster,
                topic=self.topic,
                from_beginning=(from_beginning and "--from-beginning" or ""),
            )
        )

    @mock.patch("kfk.commands.console.os")
    def test_console_producer(self, mock_os):
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
        native_command = (
            "bin/kafka-console-producer.sh --broker-list my-cluster-kafka-brokers:9092"
            " --topic {topic}"
        )
        mock_os.system.assert_called_with(
            Kubectl()
            .exec("-it", "{cluster}-kafka-0")
            .container("kafka")
            .namespace(self.namespace)
            .exec_command(native_command)
            .build()
            .format(cluster=self.cluster, topic=self.topic)
        )

    @mock.patch("kfk.commons.transfer_file_to_container")
    @mock.patch("kfk.commands.console.os")
    def test_console_producer_with_producer_config(
        self, mock_os, mock_transfer_file_to_container
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
        native_command = (
            "bin/kafka-console-producer.sh --broker-list {cluster}-kafka-brokers:9093"
            " --topic {topic} --producer.config /tmp/client.properties;rm -rf"
            " /tmp/truststore.jks;rm -rf /tmp/user.p12;rm -rf /tmp/client.properties;"
        )

        mock_os.system.assert_called_with(
            Kubectl()
            .exec("-it", "{cluster}-kafka-0")
            .container("kafka")
            .namespace(self.namespace)
            .exec_command(native_command)
            .build()
            .format(cluster=self.cluster, topic=self.topic)
        )
