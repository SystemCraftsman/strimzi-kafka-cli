from tests.integration.conftest import requires_cluster


@requires_cluster
class TestNodePools:

    def test_list_node_pools(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd, ["node-pools", "--list", "-c", cluster, "-n", namespace]
        )
        assert result.exit_code == 0
        assert "broker" in result.output

    def test_describe_node_pool(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            [
                "node-pools",
                "--describe",
                "--node-pool",
                "broker",
                "-c",
                cluster,
                "-n",
                namespace,
            ],
        )
        assert result.exit_code == 0
        assert "broker" in result.output
