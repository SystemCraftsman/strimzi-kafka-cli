import os
import tarfile
import tempfile
from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.commands.backup.commons import (
    clean_metadata,
    clean_secret_metadata,
    create_archive,
    extract_archive,
)
from kfk.main import kfk


class TestBackupHelp(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @mock.patch("kfk.setup.setup")
    def test_backup_help(self, mock_setup):
        result = self.runner.invoke(kfk, ["backup", "--help"])
        assert result.exit_code == 0
        assert "kafka" in result.output
        assert "connect" in result.output

    @mock.patch("kfk.setup.setup")
    def test_backup_kafka_help(self, mock_setup):
        result = self.runner.invoke(kfk, ["backup", "kafka", "--help"])
        assert result.exit_code == 0
        assert "--cluster" in result.output
        assert "--restore" in result.output
        assert "--from" in result.output
        assert "--include-secrets" in result.output

    @mock.patch("kfk.setup.setup")
    def test_backup_connect_help(self, mock_setup):
        result = self.runner.invoke(kfk, ["backup", "connect", "--help"])
        assert result.exit_code == 0
        assert "--cluster" in result.output
        assert "--restore" in result.output
        assert "--from" in result.output

    @mock.patch("kfk.setup.setup")
    def test_backup_kafka_requires_cluster(self, mock_setup):
        result = self.runner.invoke(kfk, ["backup", "kafka", "-n", "test"])
        assert result.exit_code != 0

    @mock.patch("kfk.setup.setup")
    def test_backup_connect_requires_cluster(self, mock_setup):
        result = self.runner.invoke(kfk, ["backup", "connect", "-n", "test"])
        assert result.exit_code != 0


class TestCleanMetadata(TestCase):
    def test_clean_metadata_strips_fields(self):
        resource = {
            "metadata": {
                "name": "my-cluster",
                "namespace": "kafka",
                "creationTimestamp": "2024-01-01T00:00:00Z",
                "generation": 1,
                "managedFields": [{"manager": "strimzi"}],
                "resourceVersion": "12345",
                "selfLink": "/apis/...",
                "uid": "abc-123",
                "annotations": {
                    "kubectl.kubernetes.io/last-applied-configuration": "{}",
                    "strimzi.io/some-annotation": "value",
                },
            },
            "spec": {"replicas": 3},
            "status": {"conditions": []},
        }
        result = clean_metadata(resource)
        assert "creationTimestamp" not in result["metadata"]
        assert "generation" not in result["metadata"]
        assert "managedFields" not in result["metadata"]
        assert "resourceVersion" not in result["metadata"]
        assert "uid" not in result["metadata"]
        assert "status" not in result
        assert result["metadata"]["name"] == "my-cluster"
        assert (
            "kubectl.kubernetes.io/last-applied-configuration"
            not in result["metadata"]["annotations"]
        )
        assert (
            result["metadata"]["annotations"]["strimzi.io/some-annotation"] == "value"
        )

    def test_clean_metadata_removes_empty_annotations(self):
        resource = {
            "metadata": {
                "name": "test",
                "annotations": {
                    "kubectl.kubernetes.io/last-applied-configuration": "{}",
                },
            },
        }
        result = clean_metadata(resource)
        assert "annotations" not in result["metadata"]

    def test_clean_metadata_strips_owner_references(self):
        resource = {
            "metadata": {
                "name": "test",
                "ownerReferences": [{"name": "parent"}],
            },
        }
        result = clean_metadata(resource)
        assert "ownerReferences" not in result["metadata"]


class TestCleanSecretMetadata(TestCase):
    def test_clean_secret_metadata_strips_fields(self):
        secret = {
            "metadata": {
                "name": "my-secret",
                "namespace": "kafka",
                "creationTimestamp": "2024-01-01T00:00:00Z",
                "resourceVersion": "999",
                "uid": "xyz",
                "owner_references": [{"name": "parent"}],
            },
            "data": {"key": "dmFsdWU="},
        }
        result = clean_secret_metadata(secret)
        assert "creationTimestamp" not in result["metadata"]
        assert "resourceVersion" not in result["metadata"]
        assert "uid" not in result["metadata"]
        assert "owner_references" not in result["metadata"]
        assert result["data"]["key"] == "dmFsdWU="


class TestArchive(TestCase):
    def test_create_and_extract_archive(self):
        resources = {
            "kafka.yaml": {
                "apiVersion": "kafka.strimzi.io/v1",
                "kind": "Kafka",
                "metadata": {"name": "my-cluster"},
                "spec": {"kafka": {"replicas": 3}},
            },
            "topics/test-topic.yaml": {
                "apiVersion": "kafka.strimzi.io/v1",
                "kind": "KafkaTopic",
                "metadata": {"name": "test-topic"},
                "spec": {"partitions": 3},
            },
        }

        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as f:
            output_path = f.name

        try:
            create_archive(resources, output_path)
            assert os.path.exists(output_path)
            assert tarfile.is_tarfile(output_path)

            extracted = extract_archive(output_path)
            assert "kafka.yaml" in extracted
            assert "topics/test-topic.yaml" in extracted
            assert extracted["kafka.yaml"]["metadata"]["name"] == "my-cluster"
            assert extracted["topics/test-topic.yaml"]["spec"]["partitions"] == 3
        finally:
            os.unlink(output_path)

    def test_extract_empty_archive(self):
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as f:
            output_path = f.name

        try:
            create_archive({}, output_path)
            extracted = extract_archive(output_path)
            assert extracted == {}
        finally:
            os.unlink(output_path)


class TestBackupKafkaCommand(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @mock.patch("kfk.setup.setup")
    @mock.patch("kfk.commands.backup.kafka.get_custom_resources")
    def test_backup_cluster_not_found(self, mock_get_resources, mock_setup):
        mock_get_resources.return_value = []
        result = self.runner.invoke(
            kfk,
            ["backup", "kafka", "--cluster", "my-cluster", "-n", "kafka"],
        )
        assert result.exit_code != 0
        assert "not found" in result.output

    @mock.patch("kfk.setup.setup")
    @mock.patch("kfk.commands.backup.kafka.create_archive")
    @mock.patch("kfk.commands.backup.kafka.get_custom_resources")
    def test_backup_kafka_success(
        self, mock_get_resources, mock_create_archive, mock_setup
    ):
        mock_get_resources.side_effect = [
            [{"metadata": {"name": "my-cluster"}, "spec": {}}],
            [],
            [],
            [],
        ]
        result = self.runner.invoke(
            kfk,
            [
                "backup",
                "kafka",
                "--cluster",
                "my-cluster",
                "-n",
                "kafka",
                "-o",
                "/tmp/test-backup.tar.gz",
            ],
        )
        assert result.exit_code == 0
        assert "Backup saved" in result.output
        mock_create_archive.assert_called_once()

    @mock.patch("kfk.setup.setup")
    @mock.patch("kfk.commands.backup.kafka.restore_custom_resource")
    @mock.patch("kfk.commands.backup.kafka.extract_archive")
    def test_restore_kafka_success(self, mock_extract, mock_restore_cr, mock_setup):
        mock_extract.return_value = {
            "kafka.yaml": {
                "kind": "Kafka",
                "metadata": {"name": "old-cluster"},
                "spec": {},
            },
            "topics/my-topic.yaml": {
                "kind": "KafkaTopic",
                "metadata": {"name": "my-topic"},
                "spec": {},
            },
        }
        result = self.runner.invoke(
            kfk,
            [
                "backup",
                "kafka",
                "--restore",
                "--from",
                "backup.tar.gz",
                "--cluster",
                "my-cluster",
                "-n",
                "kafka",
            ],
        )
        assert result.exit_code == 0
        assert "Restore complete" in result.output
        assert mock_restore_cr.call_count == 2

    @mock.patch("kfk.setup.setup")
    def test_restore_without_from_flag(self, mock_setup):
        result = self.runner.invoke(
            kfk,
            [
                "backup",
                "kafka",
                "--restore",
                "--cluster",
                "my-cluster",
                "-n",
                "kafka",
            ],
        )
        assert result.exit_code != 0
        assert "--from is required" in result.output

    @mock.patch("kfk.setup.setup")
    @mock.patch("kfk.commands.backup.kafka.restore_custom_resource")
    @mock.patch("kfk.commands.backup.kafka.extract_archive")
    def test_restore_to_different_namespace(
        self, mock_extract, mock_restore_cr, mock_setup
    ):
        mock_extract.return_value = {
            "kafka.yaml": {
                "kind": "Kafka",
                "metadata": {"name": "old-cluster", "namespace": "old-ns"},
                "spec": {},
            },
        }
        result = self.runner.invoke(
            kfk,
            [
                "backup",
                "kafka",
                "--restore",
                "--from",
                "backup.tar.gz",
                "--cluster",
                "my-cluster",
                "-n",
                "new-namespace",
            ],
        )
        assert result.exit_code == 0
        call_args = mock_restore_cr.call_args
        assert call_args[0][1] == "new-namespace"

    @mock.patch("kfk.setup.setup")
    @mock.patch("kfk.commands.backup.kafka.restore_secret")
    @mock.patch("kfk.commands.backup.kafka.restore_custom_resource")
    @mock.patch("kfk.commands.backup.kafka.extract_archive")
    def test_restore_idempotent(
        self, mock_extract, mock_restore_cr, mock_restore_secret, mock_setup
    ):
        mock_extract.return_value = {
            "kafka.yaml": {
                "kind": "Kafka",
                "metadata": {"name": "my-cluster"},
                "spec": {},
            },
            "topics/t1.yaml": {
                "kind": "KafkaTopic",
                "metadata": {"name": "t1"},
                "spec": {},
            },
            "secrets/s1.yaml": {
                "metadata": {"name": "s1"},
                "data": {},
            },
        }
        result = self.runner.invoke(
            kfk,
            [
                "backup",
                "kafka",
                "--restore",
                "--from",
                "backup.tar.gz",
                "--cluster",
                "my-cluster",
                "-n",
                "kafka",
            ],
        )
        assert result.exit_code == 0
        assert mock_restore_cr.call_count == 2
        assert mock_restore_secret.call_count == 1

    @mock.patch("kfk.setup.setup")
    @mock.patch("kfk.commands.backup.kafka.create_archive")
    @mock.patch("kfk.commands.backup.kafka.get_custom_resources")
    def test_backup_with_topics_users_nodepools(
        self, mock_get_resources, mock_create_archive, mock_setup
    ):
        mock_get_resources.side_effect = [
            [{"metadata": {"name": "my-cluster"}, "spec": {}}],
            [{"metadata": {"name": "pool-a"}, "spec": {}}],
            [
                {"metadata": {"name": "topic-1"}, "spec": {}},
                {"metadata": {"name": "topic-2"}, "spec": {}},
            ],
            [{"metadata": {"name": "user-1"}, "spec": {}}],
        ]
        result = self.runner.invoke(
            kfk,
            [
                "backup",
                "kafka",
                "--cluster",
                "my-cluster",
                "-n",
                "kafka",
                "-o",
                "/tmp/full-backup.tar.gz",
            ],
        )
        assert result.exit_code == 0
        assert "Kafka/my-cluster" in result.output
        assert "KafkaNodePool/pool-a" in result.output
        assert "KafkaTopic/topic-1" in result.output
        assert "KafkaTopic/topic-2" in result.output
        assert "KafkaUser/user-1" in result.output
        archive_resources = mock_create_archive.call_args[0][0]
        assert "kafka.yaml" in archive_resources
        assert "nodepools/pool-a.yaml" in archive_resources
        assert "topics/topic-1.yaml" in archive_resources
        assert "topics/topic-2.yaml" in archive_resources
        assert "users/user-1.yaml" in archive_resources

    @mock.patch("kfk.setup.setup")
    @mock.patch("kfk.commands.backup.kafka.create_archive")
    @mock.patch("kfk.commands.backup.kafka.get_secrets")
    @mock.patch("kfk.commands.backup.kafka.get_custom_resources")
    def test_backup_with_include_secrets(
        self, mock_get_resources, mock_get_secrets, mock_create_archive, mock_setup
    ):
        mock_get_resources.side_effect = [
            [{"metadata": {"name": "my-cluster"}, "spec": {}}],
            [],
            [],
            [{"metadata": {"name": "user-1"}, "spec": {}}],
        ]
        mock_get_secrets.side_effect = [
            [{"metadata": {"name": "my-cluster-ca-cert"}, "data": {}}],
            [{"metadata": {"name": "user-1-creds"}, "data": {}}],
        ]
        result = self.runner.invoke(
            kfk,
            [
                "backup",
                "kafka",
                "--cluster",
                "my-cluster",
                "-n",
                "kafka",
                "--include-secrets",
                "-o",
                "/tmp/secrets-backup.tar.gz",
            ],
        )
        assert result.exit_code == 0
        assert "Secret/my-cluster-ca-cert" in result.output
        assert "Secret/user-1-creds" in result.output
        archive_resources = mock_create_archive.call_args[0][0]
        assert "secrets/my-cluster-ca-cert.yaml" in archive_resources
        assert "secrets/user-1-creds.yaml" in archive_resources


class TestBackupConnectCommand(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @mock.patch("kfk.setup.setup")
    @mock.patch("kfk.commands.backup.connect.get_custom_resources")
    def test_backup_connect_not_found(self, mock_get_resources, mock_setup):
        mock_get_resources.return_value = []
        result = self.runner.invoke(
            kfk,
            [
                "backup",
                "connect",
                "--cluster",
                "my-connect",
                "-n",
                "kafka",
            ],
        )
        assert result.exit_code != 0
        assert "not found" in result.output

    @mock.patch("kfk.setup.setup")
    @mock.patch("kfk.commands.backup.connect.create_archive")
    @mock.patch("kfk.commands.backup.connect.get_custom_resources")
    def test_backup_connect_success(
        self, mock_get_resources, mock_create_archive, mock_setup
    ):
        mock_get_resources.side_effect = [
            [{"metadata": {"name": "my-connect"}, "spec": {}}],
            [],
        ]
        result = self.runner.invoke(
            kfk,
            [
                "backup",
                "connect",
                "--cluster",
                "my-connect",
                "-n",
                "kafka",
                "-o",
                "/tmp/test-connect-backup.tar.gz",
            ],
        )
        assert result.exit_code == 0
        assert "Backup saved" in result.output
        mock_create_archive.assert_called_once()

    @mock.patch("kfk.setup.setup")
    @mock.patch("kfk.commands.backup.connect.restore_custom_resource")
    @mock.patch("kfk.commands.backup.connect.extract_archive")
    def test_restore_connect_success(self, mock_extract, mock_restore_cr, mock_setup):
        mock_extract.return_value = {
            "connect.yaml": {
                "kind": "KafkaConnect",
                "metadata": {"name": "old-connect"},
                "spec": {},
            },
            "connectors/my-connector.yaml": {
                "kind": "KafkaConnector",
                "metadata": {"name": "my-connector"},
                "spec": {},
            },
        }
        result = self.runner.invoke(
            kfk,
            [
                "backup",
                "connect",
                "--restore",
                "--from",
                "backup.tar.gz",
                "--cluster",
                "my-connect",
                "-n",
                "kafka",
            ],
        )
        assert result.exit_code == 0
        assert "Restore complete" in result.output
        assert mock_restore_cr.call_count == 2
