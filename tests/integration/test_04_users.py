from tests.integration.conftest import requires_cluster

USER_NAME = "integration-test-user"


@requires_cluster
class TestUsers:

    def test_create_user(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            [
                "users",
                "--create",
                "--user",
                USER_NAME,
                "--authentication-type",
                "tls",
                "-c",
                cluster,
                "-n",
                namespace,
            ],
        )
        assert result.exit_code == 0

    def test_list_users(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd, ["users", "--list", "-c", cluster, "-n", namespace]
        )
        assert result.exit_code == 0
        assert USER_NAME in result.output

    def test_describe_user(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            [
                "users",
                "--describe",
                "--user",
                USER_NAME,
                "-c",
                cluster,
                "-n",
                namespace,
            ],
        )
        assert result.exit_code == 0
        assert USER_NAME in result.output

    def test_delete_user(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            [
                "users",
                "--delete",
                "--user",
                USER_NAME,
                "-c",
                cluster,
                "-n",
                namespace,
            ],
            input="y\n",
        )
        assert result.exit_code == 0
