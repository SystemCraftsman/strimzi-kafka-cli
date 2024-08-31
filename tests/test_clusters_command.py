from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.commands.clusters import kfk
from kfk.kubectl_command_builder import Kubectl


class TestKfkClusters(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"
        self.new_cluster_name = "my-cluster-with-new-name"

    def test_no_option(self):
        result = self.runner.invoke(
            kfk, ["clusters", "--cluster", self.cluster, "-n", self.namespace]
        )
        assert result.exit_code == 1
        assert "Missing options: kfk clusters" in result.output

    @mock.patch("kfk.commands.clusters.os")
    def test_list_clusters(self, mock_os):
        result = self.runner.invoke(kfk, ["clusters", "--list", "-n", self.namespace])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkas().namespace(self.namespace).build()
        )

    @mock.patch("kfk.commands.clusters.os")
    def test_list_clusters_all_namespaces(self, mock_os):
        result = self.runner.invoke(kfk, ["clusters", "--list"])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(Kubectl().get().kafkas().namespace().build())

    @mock.patch("kfk.commands.clusters.os")
    def test_describe_cluster(self, mock_os):
        result = self.runner.invoke(
            kfk,
            ["clusters", "--describe", "--cluster", self.cluster, "-n", self.namespace],
        )
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().describe().kafkas(self.cluster).namespace(self.namespace).build()
        )

    @mock.patch("kfk.commands.clusters.os")
    def test_describe_cluster_output_yaml(self, mock_os):
        result = self.runner.invoke(
            kfk,
            [
                "clusters",
                "--describe",
                "--cluster",
                self.cluster,
                "-n",
                self.namespace,
                "-o",
                "yaml",
            ],
        )
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl()
            .get()
            .kafkas(self.cluster)
            .namespace(self.namespace)
            .output("yaml")
            .build()
        )

    @mock.patch("kfk.commands.clusters.os")
    def test_alter_cluster_without_parameters(self, mock_os):
        result = self.runner.invoke(
            kfk,
            ["clusters", "--alter", "--cluster", self.cluster, "-n", self.namespace],
        )
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().edit().kafkas(self.cluster).namespace(self.namespace).build()
        )

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.clusters.replace_using_yaml")
    def test_alter_cluster_with_one_additional_config(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/kafka-ephemeral.yaml") as file:
            kafka_yaml = file.read()
            mock_get_resource_yaml.return_value = kafka_yaml
            result = self.runner.invoke(
                kfk,
                [
                    "clusters",
                    "--alter",
                    "--config",
                    "unclean.leader.election.enable=true",
                    "--cluster",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )
            assert result.exit_code == 0

            with open(
                "tests/files/yaml/kafka-ephemeral_with_one_additional_config.yaml"
            ) as file:
                expected_kafka_yaml = file.read()
                result_kafka_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_kafka_yaml == result_kafka_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.clusters.replace_using_yaml")
    def test_alter_cluster_with_two_additional_configs(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/kafka-ephemeral.yaml") as file:
            kafka_yaml = file.read()
            mock_get_resource_yaml.return_value = kafka_yaml
            result = self.runner.invoke(
                kfk,
                [
                    "clusters",
                    "--alter",
                    "--config",
                    "unclean.leader.election.enable=true",
                    "--config",
                    "log.retention.hours=168",
                    "--cluster",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )
            assert result.exit_code == 0

            with open(
                "tests/files/yaml/kafka-ephemeral_with_two_additional_configs.yaml"
            ) as file:
                expected_kafka_yaml = file.read()
                result_kafka_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_kafka_yaml == result_kafka_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.clusters.replace_using_yaml")
    def test_alter_cluster_with_two_additional_configs_delete_one_config(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open(
            "tests/files/yaml/kafka-ephemeral_with_two_additional_configs.yaml"
        ) as file:
            kafka_yaml = file.read()
            mock_get_resource_yaml.return_value = kafka_yaml
            result = self.runner.invoke(
                kfk,
                [
                    "clusters",
                    "--alter",
                    "--delete-config",
                    "log.retention.hours",
                    "--cluster",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )
            assert result.exit_code == 0

            with open(
                "tests/files/yaml/kafka-ephemeral_with_one_additional_config.yaml"
            ) as file:
                expected_kafka_yaml = file.read()
                result_kafka_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_kafka_yaml == result_kafka_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.clusters.replace_using_yaml")
    def test_alter_cluster_with_two_additional_configs_delete_two_configs(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open(
            "tests/files/yaml/kafka-ephemeral_with_two_additional_configs.yaml"
        ) as file:
            kafka_yaml = file.read()
            mock_get_resource_yaml.return_value = kafka_yaml
            result = self.runner.invoke(
                kfk,
                [
                    "clusters",
                    "--alter",
                    "--delete-config",
                    "log.retention.hours",
                    "--delete-config",
                    "unclean.leader.election.enable",
                    "--cluster",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )
            assert result.exit_code == 0

            with open(
                "tests/files/yaml/kafka-ephemeral_two_additional_configs_deleted.yaml"
            ) as file:
                expected_kafka_yaml = file.read()
                result_kafka_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_kafka_yaml == result_kafka_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.clusters.replace_using_yaml")
    def test_alter_cluster_with_one_replica(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/kafka-ephemeral_name_updated.yaml") as file:
            kafka_yaml = file.read()
            mock_get_resource_yaml.return_value = kafka_yaml
            result = self.runner.invoke(
                kfk,
                [
                    "clusters",
                    "--alter",
                    "--replicas",
                    1,
                    "--cluster",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )
            assert result.exit_code == 0

            with open("tests/files/yaml/kafka-ephemeral_with_one_replica.yaml") as file:
                expected_kafka_yaml = file.read()
                result_kafka_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_kafka_yaml == result_kafka_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.clusters.replace_using_yaml")
    def test_alter_cluster_with_two_replicas(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/kafka-ephemeral_name_updated.yaml") as file:
            kafka_yaml = file.read()
            mock_get_resource_yaml.return_value = kafka_yaml
            result = self.runner.invoke(
                kfk,
                [
                    "clusters",
                    "--alter",
                    "--replicas",
                    2,
                    "--cluster",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )
            assert result.exit_code == 0

            with open(
                "tests/files/yaml/kafka-ephemeral_with_two_replicas.yaml"
            ) as file:
                expected_kafka_yaml = file.read()
                result_kafka_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_kafka_yaml == result_kafka_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.clusters.replace_using_yaml")
    def test_alter_cluster_with_one_replica_one_zk_replica(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/kafka-ephemeral_name_updated.yaml") as file:
            kafka_yaml = file.read()
            mock_get_resource_yaml.return_value = kafka_yaml
            result = self.runner.invoke(
                kfk,
                [
                    "clusters",
                    "--alter",
                    "--replicas",
                    1,
                    "--zk-replicas",
                    1,
                    "--cluster",
                    self.cluster,
                    "-n",
                    self.namespace,
                ],
            )
            assert result.exit_code == 0

            with open(
                "tests/files/yaml/kafka-ephemeral_with_one_replica_one_zk_replica.yaml"
            ) as file:
                expected_kafka_yaml = file.read()
                result_kafka_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_kafka_yaml == result_kafka_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.click.confirm")
    @mock.patch("kfk.commands.clusters.delete_using_yaml")
    def test_delete_cluster(self, mock_delete_using_yaml, mock_click_confirm):
        mock_click_confirm.return_value = True
        result = self.runner.invoke(
            kfk,
            ["clusters", "--delete", "--cluster", self.cluster, "-n", self.namespace],
        )
        assert result.exit_code == 0
        mock_delete_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.click.confirm")
    @mock.patch("kfk.commands.clusters.delete_using_yaml")
    def test_delete_cluster_with_yes_flag(
        self, mock_delete_using_yaml, mock_click_confirm
    ):
        mock_click_confirm.return_value = False
        result = self.runner.invoke(
            kfk,
            [
                "clusters",
                "--delete",
                "--cluster",
                self.cluster,
                "-n",
                self.namespace,
                "-y",
            ],
        )
        assert result.exit_code == 0

        mock_delete_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commands.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.clusters.click.confirm")
    @mock.patch("kfk.commands.clusters.create_using_yaml")
    def test_create_cluster(
        self,
        mock_create_using_yaml,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
    ):
        mock_click_confirm.return_value = True

        result = self.runner.invoke(
            kfk,
            [
                "clusters",
                "--create",
                "--cluster",
                self.new_cluster_name,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        with open("tests/files/yaml/kafka-ephemeral_name_updated.yaml") as file:
            expected_kafka_yaml = file.read()
            result_kafka_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_kafka_yaml == result_kafka_yaml

        mock_create_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commands.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.clusters.click.confirm")
    @mock.patch("kfk.commands.clusters.create_using_yaml")
    def test_create_cluster_with_yes_flag(
        self,
        mock_create_using_yaml,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
    ):
        mock_click_confirm.return_value = False

        result = self.runner.invoke(
            kfk,
            [
                "clusters",
                "--create",
                "--cluster",
                self.new_cluster_name,
                "-n",
                self.namespace,
                "-y",
            ],
        )
        assert result.exit_code == 0

        mock_open_file_in_system_editor.assert_not_called()
        with open("tests/files/yaml/kafka-ephemeral_name_updated.yaml") as file:
            expected_kafka_yaml = file.read()
            result_kafka_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_kafka_yaml == result_kafka_yaml

        mock_create_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commands.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.clusters.click.confirm")
    @mock.patch("kfk.commands.clusters.create_using_yaml")
    def test_create_cluster_with_one_replica(
        self,
        mock_create_using_yaml,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
    ):
        mock_click_confirm.return_value = True

        result = self.runner.invoke(
            kfk,
            [
                "clusters",
                "--create",
                "--cluster",
                self.new_cluster_name,
                "--replicas",
                1,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        with open("tests/files/yaml/kafka-ephemeral_with_one_replica.yaml") as file:
            expected_kafka_yaml = file.read()
            result_kafka_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_kafka_yaml == result_kafka_yaml

        mock_create_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commands.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.clusters.click.confirm")
    @mock.patch("kfk.commands.clusters.create_using_yaml")
    def test_create_cluster_with_two_replicas(
        self,
        mock_create_using_yaml,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
    ):
        mock_click_confirm.return_value = True

        result = self.runner.invoke(
            kfk,
            [
                "clusters",
                "--create",
                "--cluster",
                self.new_cluster_name,
                "--replicas",
                2,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        with open("tests/files/yaml/kafka-ephemeral_with_two_replicas.yaml") as file:
            expected_kafka_yaml = file.read()
            result_kafka_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_kafka_yaml == result_kafka_yaml

        mock_create_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commands.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.clusters.click.confirm")
    @mock.patch("kfk.commands.clusters.create_using_yaml")
    def test_create_cluster_with_three_replicas(
        self,
        mock_create_using_yaml,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
    ):
        mock_click_confirm.return_value = True

        result = self.runner.invoke(
            kfk,
            [
                "clusters",
                "--create",
                "--cluster",
                self.new_cluster_name,
                "--replicas",
                3,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        with open("tests/files/yaml/kafka-ephemeral_name_updated.yaml") as file:
            expected_kafka_yaml = file.read()
            result_kafka_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_kafka_yaml == result_kafka_yaml

        mock_create_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.clusters.create_temp_file")
    @mock.patch("kfk.commands.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.clusters.click.confirm")
    @mock.patch("kfk.commands.clusters.create_using_yaml")
    def test_create_cluster_with_one_replica_one_zk_replica(
        self,
        mock_create_using_yaml,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
    ):
        mock_click_confirm.return_value = True

        result = self.runner.invoke(
            kfk,
            [
                "clusters",
                "--create",
                "--cluster",
                self.new_cluster_name,
                "--replicas",
                1,
                "--zk-replicas",
                1,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        with open(
            "tests/files/yaml/kafka-ephemeral_with_one_replica_one_zk_replica.yaml"
        ) as file:
            expected_kafka_yaml = file.read()
            result_kafka_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_kafka_yaml == result_kafka_yaml

        mock_create_using_yaml.assert_called_once()
