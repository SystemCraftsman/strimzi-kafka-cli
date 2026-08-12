import os

from tests.integration.conftest import requires_cluster


@requires_cluster
class TestBackup:
    def test_backup_kafka(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            [
                "backup",
                "kafka",
                "--cluster",
                cluster,
                "-n",
                namespace,
                "-o",
                "/tmp/integration-backup.tar.gz",
            ],
        )
        assert result.exit_code == 0
        assert "Backup saved" in result.output
        assert os.path.exists("/tmp/integration-backup.tar.gz")

    def test_backup_kafka_with_secrets(self, runner, kfk_cmd, cluster, namespace):
        result = runner.invoke(
            kfk_cmd,
            [
                "backup",
                "kafka",
                "--cluster",
                cluster,
                "-n",
                namespace,
                "--include-secrets",
                "-o",
                "/tmp/integration-backup-secrets.tar.gz",
            ],
        )
        assert result.exit_code == 0
        assert "Backup saved" in result.output
        assert "Secret/" in result.output

    def test_backup_archive_contains_resources(
        self, runner, kfk_cmd, cluster, namespace
    ):
        from kfk.commands.backup.commons import extract_archive

        resources = extract_archive("/tmp/integration-backup.tar.gz")
        assert "kafka.yaml" in resources
        assert resources["kafka.yaml"]["metadata"]["name"] == cluster
        assert len(resources) >= 1

    def test_backup_cluster_not_found(self, runner, kfk_cmd, namespace):
        result = runner.invoke(
            kfk_cmd,
            [
                "backup",
                "kafka",
                "--cluster",
                "nonexistent-cluster",
                "-n",
                namespace,
            ],
        )
        assert result.exit_code != 0
        assert "not found" in result.output
