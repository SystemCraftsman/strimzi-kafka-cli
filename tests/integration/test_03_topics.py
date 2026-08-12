from tests.integration.conftest import requires_cluster

TOPIC_NAME = "integration-test-topic"


@requires_cluster
class TestTopics:
    def test_create_topic(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            [
                "topics",
                "--create",
                "--topic",
                TOPIC_NAME,
                "--partitions",
                "1",
                "--replication-factor",
                "1",
                "-c",
                cluster,
                "-n",
                namespace,
            ],
        )
        assert result.exit_code == 0

    def test_list_topics(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd, ["topics", "--list", "-c", cluster, "-n", namespace]
        )
        assert result.exit_code == 0
        assert TOPIC_NAME in result.output

    def test_describe_topic(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            [
                "topics",
                "--describe",
                "--topic",
                TOPIC_NAME,
                "-c",
                cluster,
                "-n",
                namespace,
            ],
        )
        assert result.exit_code == 0
        assert TOPIC_NAME in result.output

    def test_alter_topic_partitions(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            [
                "topics",
                "--alter",
                "--topic",
                TOPIC_NAME,
                "--partitions",
                "3",
                "-c",
                cluster,
                "-n",
                namespace,
            ],
        )
        assert result.exit_code == 0

    def test_delete_topic(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            [
                "topics",
                "--delete",
                "--topic",
                TOPIC_NAME,
                "-c",
                cluster,
                "-n",
                namespace,
            ],
            input="y\n",
        )
        assert result.exit_code == 0
