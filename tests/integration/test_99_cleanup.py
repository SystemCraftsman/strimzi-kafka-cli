from tests.integration.conftest import requires_cluster


@requires_cluster
class TestCleanup:
    def test_delete_cluster(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            ["clusters", "--delete", "--cluster", cluster, "-n", namespace],
            input="y\n",
        )
        assert result.exit_code == 0

    def test_uninstall_operator(self, runner, kfk_cmd, namespace):
        result = runner.invoke(
            kfk_cmd,
            ["operator", "--uninstall", "-n", namespace],
        )
        assert result.exit_code == 0
