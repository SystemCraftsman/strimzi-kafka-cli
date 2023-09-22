from unittest import TestCase, mock

import click
from click.testing import CliRunner

from kfk.commands.connect.clusters import connect
from kfk.kubectl_command_builder import Kubectl


class TestKfkConnect(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-connect-cluster"
        self.namespace = "kafka"
        self.connect_config_file = "files/connect.properties"
        self.connector_config_file_1 = "files/twitter-connector.properties"
        self.connector_config_file_2 = "files/file-stream-connector.properties"
        self.registry_userpass = "someuserpass"
        self.registry_server = "quay.io/systemcraftsman/test-connect-cluster:latest"
        self.push_secret_name = f"{self.cluster}-push-secret"

    def test_no_option(self):
        result = self.runner.invoke(
            connect, ["clusters", "--cluster", self.cluster, "-n", self.namespace]
        )
        assert result.exit_code == 0
        assert "Missing options: kfk connect" in result.output

    def test_create_custer_without_config_file(self):
        result = self.runner.invoke(
            connect,
            ["clusters", "--create", "--cluster", self.cluster, "-n", self.namespace],
        )

        assert result.exit_code == 2

    @mock.patch("kfk.commands.connect.clusters.click.prompt")
    @mock.patch("kfk.commands.connect.clusters.create_temp_file")
    @mock.patch("kfk.commands.connect.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.connect.clusters.click.confirm")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_create_cluster(
        self,
        mock_os,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
        mock_click_prompt,
    ):
        mock_click_confirm.return_value = True
        mock_click_prompt.return_value = self.registry_userpass

        result = self.runner.invoke(
            connect,
            [
                "clusters",
                "--create",
                "--cluster",
                self.cluster,
                self.connect_config_file,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        result_connect_yaml = mock_create_temp_file.call_args[0][0]

        with open(r"files/yaml/kafka-connect.yaml") as file:
            expected_connect_yaml = file.read()

            assert expected_connect_yaml == result_connect_yaml

        mock_os.system.assert_any_call(
            Kubectl()
            .create()
            .secret(
                "docker-registry",
                self.push_secret_name,
                "--docker-username={username}",
                "--docker-password={password} --docker-server={registry_server}",
            )
            .namespace(self.namespace)
            .build()
            .format(
                username=self.registry_userpass,
                password=self.registry_userpass,
                registry_server=self.registry_server,
            )
        )

    @mock.patch("kfk.commands.connect.clusters.click.prompt")
    @mock.patch("kfk.commands.connect.clusters.create_temp_file")
    @mock.patch("kfk.commands.connect.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.connect.clusters.click.confirm")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_create_cluster_with_image(
        self,
        mock_os,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
        mock_click_prompt,
    ):
        mock_click_confirm.return_value = True
        mock_click_prompt.return_value = self.registry_userpass

        result = self.runner.invoke(
            connect,
            [
                "clusters",
                "--create",
                "--cluster",
                self.cluster,
                "files/connect_with_only_image.properties",
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        result_connect_yaml = mock_create_temp_file.call_args[0][0]

        with open(r"files/yaml/kafka-connect_with_image.yaml") as file:
            expected_connect_yaml = file.read()

            assert expected_connect_yaml == result_connect_yaml

        try:
            mock_os.system.assert_any_call(
                Kubectl()
                .create()
                .secret(
                    "docker-registry",
                    self.push_secret_name,
                    "--docker-username={username}",
                    "--docker-password={password} --docker-server={registry_server}",
                )
                .namespace(self.namespace)
                .build()
                .format(
                    username=self.registry_userpass,
                    password=self.registry_userpass,
                    registry_server=self.registry_server,
                )
            )
        except Exception:
            self.assertRaises(AssertionError)

    @mock.patch("kfk.commands.connect.clusters.click.prompt")
    @mock.patch("kfk.commands.connect.clusters.create_temp_file")
    @mock.patch("kfk.commands.connect.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.connect.clusters.click.confirm")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_create_cluster_with_command_error(
        self,
        mock_os,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
        mock_click_prompt,
    ):
        mock_click_confirm.return_value = True
        mock_click_prompt.return_value = self.registry_userpass
        mock_os.system.return_value = 1

        result = self.runner.invoke(
            connect,
            [
                "clusters",
                "--create",
                "--cluster",
                self.cluster,
                self.connect_config_file,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        assert mock_os.system.call_count == 1

    @mock.patch("kfk.commands.connect.clusters.click.prompt")
    @mock.patch("kfk.commands.connect.clusters.create_temp_file")
    @mock.patch("kfk.commands.connect.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.connect.clusters.click.confirm")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_create_cluster_with_zip_jar_plugins(
        self,
        mock_os,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
        mock_click_prompt,
    ):
        mock_click_confirm.return_value = True
        mock_click_prompt.return_value = self.registry_userpass

        result = self.runner.invoke(
            connect,
            [
                "clusters",
                "--create",
                "--cluster",
                self.cluster,
                "files/connect_with_zip_jar_plugins.properties",
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        result_connect_yaml = mock_create_temp_file.call_args[0][0]

        with open(r"files/yaml/kafka-connect_with_zip_jar_plugins.yaml") as file:
            expected_connect_yaml = file.read()

            assert expected_connect_yaml == result_connect_yaml

        mock_os.system.assert_any_call(
            Kubectl()
            .create()
            .secret(
                "docker-registry",
                self.push_secret_name,
                "--docker-username={username}",
                "--docker-password={password} --docker-server={registry_server}",
            )
            .namespace(self.namespace)
            .build()
            .format(
                username=self.registry_userpass,
                password=self.registry_userpass,
                registry_server=self.registry_server,
            )
        )

    @mock.patch("kfk.commands.connect.clusters.click.prompt")
    @mock.patch("kfk.commands.connect.clusters.create_temp_file")
    @mock.patch("kfk.commands.connect.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.connect.clusters.click.confirm")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_create_cluster_with_invalid_url(
        self,
        mock_os,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
        mock_click_prompt,
    ):
        mock_click_confirm.return_value = True
        mock_click_prompt.return_value = self.registry_userpass

        result = self.runner.invoke(
            connect,
            [
                "clusters",
                "--create",
                "--cluster",
                self.cluster,
                "files/connect_with_invalid_url.properties",
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 1

        self.assertRaises(click.ClickException)

    @mock.patch("kfk.commands.connect.clusters.click.prompt")
    @mock.patch("kfk.commands.connect.clusters.create_temp_file")
    @mock.patch("kfk.commands.connect.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.connect.clusters.click.confirm")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_create_cluster_with_yes_flag(
        self,
        mock_os,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
        mock_click_prompt,
    ):
        mock_click_confirm.return_value = False
        mock_click_prompt.return_value = self.registry_userpass

        result = self.runner.invoke(
            connect,
            [
                "clusters",
                "--create",
                "--cluster",
                self.cluster,
                self.connect_config_file,
                "-n",
                self.namespace,
                "-y",
            ],
        )
        assert result.exit_code == 0

        with open(r"files/yaml/kafka-connect.yaml") as file:
            expected_connect_yaml = file.read()
            result_connect_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_connect_yaml == result_connect_yaml

        mock_os.system.assert_any_call(
            Kubectl()
            .create()
            .secret(
                "docker-registry",
                self.push_secret_name,
                "--docker-username={username}",
                "--docker-password={password} --docker-server={registry_server}",
            )
            .namespace(self.namespace)
            .build()
            .format(
                username=self.registry_userpass,
                password=self.registry_userpass,
                registry_server=self.registry_server,
            )
        )

    @mock.patch("kfk.commands.connect.clusters.click.prompt")
    @mock.patch("kfk.commands.connect.clusters.create_temp_file")
    @mock.patch("kfk.commands.connect.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.connect.clusters.click.confirm")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_create_cluster_three_replicas(
        self,
        mock_os,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
        mock_click_prompt,
    ):
        mock_click_confirm.return_value = True
        mock_click_prompt.return_value = self.registry_userpass

        result = self.runner.invoke(
            connect,
            [
                "clusters",
                "--create",
                "--cluster",
                self.cluster,
                "--replicas",
                3,
                self.connect_config_file,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        with open(r"files/yaml/kafka-connect_with_three_replicas.yaml") as file:
            expected_connect_yaml = file.read()
            result_connect_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_connect_yaml == result_connect_yaml

        mock_os.system.assert_any_call(
            Kubectl()
            .create()
            .secret(
                "docker-registry",
                self.push_secret_name,
                "--docker-username={username}",
                "--docker-password={password} --docker-server={registry_server}",
            )
            .namespace(self.namespace)
            .build()
            .format(
                username=self.registry_userpass,
                password=self.registry_userpass,
                registry_server=self.registry_server,
            )
        )

    @mock.patch("kfk.commands.connect.connectors.create_temp_file")
    @mock.patch("kfk.commands.connect.connectors.os")
    @mock.patch("kfk.commands.connect.clusters.click.prompt")
    @mock.patch("kfk.commands.connect.clusters.create_temp_file")
    @mock.patch("kfk.commands.connect.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.connect.clusters.click.confirm")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_create_cluster_with_connector_config(
        self,
        mock_os,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
        mock_click_prompt,
        mock_os_connectors,
        mock_create_temp_file_connectors,
    ):
        mock_click_confirm.return_value = True
        mock_click_prompt.return_value = self.registry_userpass
        mock_os.system.return_value = 0

        result = self.runner.invoke(
            connect,
            [
                "clusters",
                "--create",
                "--cluster",
                self.cluster,
                self.connect_config_file,
                self.connector_config_file_1,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        with open(r"files/yaml/kafka-connect.yaml") as file:
            expected_connect_yaml = file.read()
            result_connect_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_connect_yaml == result_connect_yaml

        mock_os.system.assert_any_call(
            Kubectl()
            .create()
            .secret(
                "docker-registry",
                self.push_secret_name,
                "--docker-username={username}",
                "--docker-password={password} --docker-server={registry_server}",
            )
            .namespace(self.namespace)
            .build()
            .format(
                username=self.registry_userpass,
                password=self.registry_userpass,
                registry_server=self.registry_server,
            )
        )

        with open(r"files/yaml/kafka-connect-connector-twitter.yaml") as file:
            expected_connector_yaml = file.read()
            result_connector_yaml = mock_create_temp_file_connectors.call_args[0][0]
            assert expected_connector_yaml == result_connector_yaml

    @mock.patch("kfk.commands.connect.connectors.create_temp_file")
    @mock.patch("kfk.commands.connect.connectors.os")
    @mock.patch("kfk.commands.connect.clusters.click.prompt")
    @mock.patch("kfk.commands.connect.clusters.create_temp_file")
    @mock.patch("kfk.commands.connect.clusters.open_file_in_system_editor")
    @mock.patch("kfk.commands.connect.clusters.click.confirm")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_create_cluster_with_two_connectors_config(
        self,
        mock_os,
        mock_click_confirm,
        mock_open_file_in_system_editor,
        mock_create_temp_file,
        mock_click_prompt,
        mock_os_connectors,
        mock_create_temp_file_connectors,
    ):
        mock_click_confirm.return_value = True
        mock_click_prompt.return_value = self.registry_userpass
        mock_os.system.return_value = 0

        result = self.runner.invoke(
            connect,
            [
                "clusters",
                "--create",
                "--cluster",
                self.cluster,
                self.connect_config_file,
                self.connector_config_file_1,
                self.connector_config_file_2,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        with open(r"files/yaml/kafka-connect.yaml") as file:
            expected_connect_yaml = file.read()
            result_connect_yaml = mock_create_temp_file.call_args[0][0]
            assert expected_connect_yaml == result_connect_yaml

        mock_os.system.assert_any_call(
            Kubectl()
            .create()
            .secret(
                "docker-registry",
                self.push_secret_name,
                "--docker-username={username}",
                "--docker-password={password} --docker-server={registry_server}",
            )
            .namespace(self.namespace)
            .build()
            .format(
                username=self.registry_userpass,
                password=self.registry_userpass,
                registry_server=self.registry_server,
            )
        )

        with open(r"files/yaml/kafka-connect-connector-twitter.yaml") as file:
            expected_connector_yaml = file.read()
            result_connector_yaml = mock_create_temp_file_connectors.call_args_list[0][
                0
            ][0]
            assert expected_connector_yaml == result_connector_yaml

        with open(r"files/yaml/kafka-connect-connector-file-stream.yaml") as file:
            expected_connector_yaml = file.read()
            result_connector_yaml = mock_create_temp_file_connectors.call_args_list[1][
                0
            ][0]
            assert expected_connector_yaml == result_connector_yaml

    @mock.patch("kfk.commands.connect.clusters.os")
    def test_list_clusters(self, mock_os):
        result = self.runner.invoke(
            connect, ["clusters", "--list", "-n", self.namespace]
        )
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkaconnects().namespace(self.namespace).build()
        )

    @mock.patch("kfk.commands.connect.clusters.os")
    def test_list_clusters_all_namespaces(self, mock_os):
        result = self.runner.invoke(connect, ["clusters", "--list"])
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl().get().kafkaconnects().namespace().build()
        )

    @mock.patch("kfk.commands.connect.clusters.os")
    def test_describe_cluster(self, mock_os):
        result = self.runner.invoke(
            connect,
            ["clusters", "--describe", "--cluster", self.cluster, "-n", self.namespace],
        )
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl()
            .describe()
            .kafkaconnects(self.cluster)
            .namespace(self.namespace)
            .build()
        )

    @mock.patch("kfk.commands.connect.clusters.os")
    def test_describe_cluster_output_yaml(self, mock_os):
        result = self.runner.invoke(
            connect,
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
            .kafkaconnects(self.cluster)
            .namespace(self.namespace)
            .output("yaml")
            .build()
        )

    @mock.patch("kfk.commands.connect.clusters.click.confirm")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_delete_cluster(self, mock_os, mock_click_confirm):
        mock_click_confirm.return_value = True
        result = self.runner.invoke(
            connect,
            ["clusters", "--delete", "--cluster", self.cluster, "-n", self.namespace],
        )
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl()
            .delete()
            .kafkaconnects(self.cluster)
            .namespace(self.namespace)
            .build()
        )

    @mock.patch("kfk.commands.connect.clusters.click.confirm")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_delete_cluster_with_yes_flag(self, mock_os, mock_click_confirm):
        mock_click_confirm.return_value = False
        result = self.runner.invoke(
            connect,
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
        mock_os.system.assert_called_with(
            Kubectl()
            .delete()
            .kafkaconnects(self.cluster)
            .namespace(self.namespace)
            .build()
        )

    @mock.patch("kfk.commands.connect.clusters.os")
    def test_alter_cluster_without_parameters(self, mock_os):
        result = self.runner.invoke(
            connect,
            ["clusters", "--alter", "--cluster", self.cluster, "-n", self.namespace],
        )
        assert result.exit_code == 0
        mock_os.system.assert_called_with(
            Kubectl()
            .edit()
            .kafkaconnects(self.cluster)
            .namespace(self.namespace)
            .build()
        )

    @mock.patch("kfk.commands.connect.clusters.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_alter_cluster_with_replica_param(
        self, mock_os, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open(r"files/yaml/kafka-connect.yaml") as file:
            connect_yaml = file.read()

            mock_get_resource_yaml.return_value = connect_yaml

            result = self.runner.invoke(
                connect,
                [
                    "clusters",
                    "--alter",
                    "--cluster",
                    self.cluster,
                    "--replicas",
                    3,
                    "-n",
                    self.namespace,
                ],
            )
            assert result.exit_code == 0

            with open(r"files/yaml/kafka-connect_with_three_replicas.yaml") as file:
                expected_connect_yaml = file.read()
                result_connect_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_connect_yaml == result_connect_yaml

    @mock.patch("kfk.commands.connect.clusters.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_alter_cluster_with_different_config_file(
        self, mock_os, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open(r"files/yaml/kafka-connect.yaml") as file:
            connect_yaml = file.read()

            mock_get_resource_yaml.return_value = connect_yaml

            result = self.runner.invoke(
                connect,
                [
                    "clusters",
                    "--alter",
                    "--cluster",
                    self.cluster,
                    "files/connect_with_zip_jar_plugins.properties",
                    "-n",
                    self.namespace,
                ],
            )
            assert result.exit_code == 0

            with open(r"files/yaml/kafka-connect_with_zip_jar_plugins.yaml") as file:
                expected_connect_yaml = file.read()
                result_connect_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_connect_yaml == result_connect_yaml

    @mock.patch("kfk.commands.connect.clusters.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.connect.clusters.os")
    def test_alter_cluster_with_only_image_config_file(
        self, mock_os, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open(r"files/yaml/kafka-connect.yaml") as file:
            connect_yaml = file.read()

            mock_get_resource_yaml.return_value = connect_yaml

            result = self.runner.invoke(
                connect,
                [
                    "clusters",
                    "--alter",
                    "--cluster",
                    self.cluster,
                    "files/connect_with_only_image.properties",
                    "-n",
                    self.namespace,
                ],
            )
            assert result.exit_code == 0

            with open(r"files/yaml/kafka-connect_with_image.yaml") as file:
                expected_connect_yaml = file.read()
                result_connect_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_connect_yaml == result_connect_yaml
