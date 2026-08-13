import os

from tests.integration.conftest import requires_cluster

MCP_TOPIC = "mcp-test-topic"
MCP_USER = "mcp-test-user"


@requires_cluster
class TestMcpKafka:
    def test_list_kafkas(self, cluster, namespace):
        from kfk.mcp_server import list_kafkas

        result = list_kafkas(namespace)
        names = [item["metadata"]["name"] for item in result["items"]]
        assert cluster in names

    def test_get_kafka(self, cluster, namespace):
        from kfk.mcp_server import get_kafka

        result = get_kafka(cluster, namespace)
        assert result["metadata"]["name"] == cluster

    def test_get_kafka_status(self, cluster, namespace):
        from kfk.mcp_server import get_kafka_status

        result = get_kafka_status(cluster, namespace)
        assert isinstance(result, dict)

    def test_alter_kafka_config(self, cluster, namespace):
        from kfk.mcp_server import alter_kafka_config

        result = alter_kafka_config(
            cluster,
            namespace,
            config=["log.retention.hours=168"],
        )
        assert result is not None


@requires_cluster
class TestMcpTopics:
    def test_create_topic(self, cluster, namespace):
        from kfk.mcp_server import create_topic

        result = create_topic(
            MCP_TOPIC,
            cluster,
            namespace,
            partitions=1,
            replication_factor=1,
        )
        assert result is not None

    def test_list_topics(self, cluster, namespace):
        from kfk.mcp_server import list_topics

        result = list_topics(cluster, namespace)
        names = [item["metadata"]["name"] for item in result["items"]]
        assert MCP_TOPIC in names

    def test_get_topic(self, cluster, namespace):
        from kfk.mcp_server import get_topic

        result = get_topic(MCP_TOPIC, cluster, namespace)
        assert result["metadata"]["name"] == MCP_TOPIC

    def test_alter_topic(self, cluster, namespace):
        from kfk.mcp_server import alter_topic

        result = alter_topic(
            MCP_TOPIC,
            cluster,
            namespace,
            partitions=3,
        )
        assert result is not None

    def test_alter_topic_config(self, cluster, namespace):
        from kfk.mcp_server import alter_topic

        result = alter_topic(
            MCP_TOPIC,
            cluster,
            namespace,
            config=["retention.ms=86400000"],
        )
        assert result is not None

    def test_delete_topic(self, cluster, namespace):
        from kfk.mcp_server import delete_topic

        result = delete_topic(MCP_TOPIC, cluster, namespace)
        assert result is not None


@requires_cluster
class TestMcpUsers:
    def test_create_user(self, cluster, namespace):
        from kfk.mcp_server import create_user

        result = create_user(
            MCP_USER,
            cluster,
            namespace,
            authentication_type="tls",
        )
        assert result is not None

    def test_list_users(self, cluster, namespace):
        from kfk.mcp_server import list_users

        result = list_users(cluster, namespace)
        names = [item["metadata"]["name"] for item in result["items"]]
        assert MCP_USER in names

    def test_get_user(self, cluster, namespace):
        from kfk.mcp_server import get_user

        result = get_user(MCP_USER, cluster, namespace)
        assert result["metadata"]["name"] == MCP_USER

    def test_alter_user(self, cluster, namespace):
        from kfk.mcp_server import alter_user

        result = alter_user(
            MCP_USER,
            cluster,
            namespace,
            authentication_type="scram-sha-512",
        )
        assert result is not None

    def test_delete_user(self, cluster, namespace):
        from kfk.mcp_server import delete_user

        result = delete_user(MCP_USER, cluster, namespace)
        assert result is not None


@requires_cluster
class TestMcpNodePools:
    def test_list_node_pools(self, cluster, namespace):
        from kfk.mcp_server import list_node_pools

        result = list_node_pools(cluster, namespace)
        names = [item["metadata"]["name"] for item in result["items"]]
        assert "broker" in names

    def test_get_node_pool(self, cluster, namespace, capsys):
        from kfk.mcp_server import get_node_pool

        get_node_pool("broker", cluster, namespace)
        captured = capsys.readouterr()
        assert "broker" in captured.out


@requires_cluster
class TestMcpBackup:
    def test_backup_kafka(self, cluster, namespace):
        from kfk.mcp_server import backup_kafka

        output = "/tmp/mcp-integration-backup.tar.gz"
        result = backup_kafka(cluster, namespace, output=output)
        assert "Backup saved" in result
        assert os.path.exists(output)

    def test_backup_kafka_with_secrets(self, cluster, namespace):
        from kfk.mcp_server import backup_kafka

        output = "/tmp/mcp-integration-backup-secrets.tar.gz"
        result = backup_kafka(cluster, namespace, output=output, include_secrets=True)
        assert "Backup saved" in result

    def test_restore_kafka(self, cluster, namespace):
        from kfk.mcp_server import restore_kafka

        result = restore_kafka("/tmp/mcp-integration-backup.tar.gz", cluster, namespace)
        assert "Restored" in result

    def test_backup_cluster_not_found(self, namespace):
        from kfk.mcp_server import backup_kafka

        result = backup_kafka("nonexistent-cluster", namespace)
        assert "not found" in result


@requires_cluster
class TestMcpVersion:
    def test_get_version(self):
        from kfk.mcp_server import get_version

        result = get_version()
        assert "CLI Version" in result
