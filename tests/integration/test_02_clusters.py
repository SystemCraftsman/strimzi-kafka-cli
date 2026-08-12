from tests.integration.conftest import requires_cluster, wait_for_resource


@requires_cluster
class TestClusters:
    def test_create_cluster(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            ["clusters", "--create", "--cluster", cluster, "-n", namespace, "-y"],
        )
        assert result.exit_code == 0

    def test_cluster_is_ready(self, cluster, namespace):
        assert wait_for_resource("kafka", cluster, namespace, timeout=300), (
            "Kafka cluster did not become ready"
        )

    def test_list_clusters(self, runner, kfk_cmd, namespace):
        result = runner.invoke(kfk_cmd, ["clusters", "--list", "-n", namespace])
        assert result.exit_code == 0
        assert "my-cluster" in result.output

    def test_describe_cluster(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            ["clusters", "--describe", "--cluster", cluster, "-n", namespace],
        )
        assert result.exit_code == 0
        assert cluster in result.output

    def test_no_option_shows_error(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            ["clusters", "--cluster", cluster, "-n", namespace],
        )
        assert result.exit_code == 1
