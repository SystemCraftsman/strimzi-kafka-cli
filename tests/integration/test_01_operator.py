import subprocess

from tests.integration.conftest import requires_cluster, wait_for_deployment


@requires_cluster
class TestOperatorInstall:

    def test_create_namespace(self, namespace):
        result = subprocess.run(
            ["kubectl", "create", "namespace", namespace],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_install_operator(self, runner, kfk_cmd, namespace):
        result = runner.invoke(
            kfk_cmd,
            ["operator", "--install", "-n", namespace],
        )
        assert result.exit_code == 0

    def test_operator_is_running(self, namespace):
        assert wait_for_deployment(
            "strimzi-cluster-operator", namespace, timeout=300
        ), "Strimzi operator did not become ready"
