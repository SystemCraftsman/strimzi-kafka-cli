from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.commands.acls import kfk
from kfk.kubectl_command_builder import Kubectl


class TestKfkAcls(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.kafka_cluster = "my-cluster"
        self.namespace = "kafka"
        self.topic = "my-topic"
        self.group = "my-group"
        self.user = "my-user"

    @mock.patch("kfk.commands.acls.os")
    def test_list_all_acls(self, mock_os):
        result = self.runner.invoke(
            kfk, ["acls", "--list", "-n", self.namespace, "-c", self.kafka_cluster]
        )
        assert result.exit_code == 0
        native_command = (
            "bin/kafka-acls.sh --authorizer-properties"
            " zookeeper.connect=localhost:12181 --list  "
        )
        mock_os.system.assert_called_with(
            Kubectl()
            .exec("-it", "{kafka_cluster}-zookeeper-0")
            .container("zookeeper")
            .namespace(self.namespace)
            .exec_command(native_command)
            .build()
            .format(kafka_cluster=self.kafka_cluster)
        )

    @mock.patch("kfk.commands.acls.os")
    def test_list_topic_acls(self, mock_os):
        result = self.runner.invoke(
            kfk,
            [
                "acls",
                "--list",
                "--topic",
                self.topic,
                "-n",
                self.namespace,
                "-c",
                self.kafka_cluster,
            ],
        )
        assert result.exit_code == 0
        native_command = (
            "bin/kafka-acls.sh --authorizer-properties"
            " zookeeper.connect=localhost:12181 --list --topic {topic} ".format(
                topic=self.topic
            )
        )
        mock_os.system.assert_called_with(
            Kubectl()
            .exec("-it", "{kafka_cluster}-zookeeper-0")
            .container("zookeeper")
            .namespace(self.namespace)
            .exec_command(native_command)
            .build()
            .format(kafka_cluster=self.kafka_cluster)
        )

    @mock.patch("kfk.commands.acls.os")
    def test_list_group_acls(self, mock_os):
        result = self.runner.invoke(
            kfk,
            [
                "acls",
                "--list",
                "--group",
                self.group,
                "-n",
                self.namespace,
                "-c",
                self.kafka_cluster,
            ],
        )
        assert result.exit_code == 0
        native_command = (
            "bin/kafka-acls.sh --authorizer-properties"
            " zookeeper.connect=localhost:12181 --list  --group {group}".format(
                group=self.group
            )
        )
        mock_os.system.assert_called_with(
            Kubectl()
            .exec("-it", "{kafka_cluster}-zookeeper-0")
            .container("zookeeper")
            .namespace(self.namespace)
            .exec_command(native_command)
            .build()
            .format(kafka_cluster=self.kafka_cluster)
        )

    @mock.patch("kfk.commands.acls.os")
    def test_add_acls_without_principal(self, mock_os):
        result = self.runner.invoke(
            kfk,
            [
                "acls",
                "--add",
                "--topic",
                self.topic,
                "-n",
                self.namespace,
                "-c",
                self.kafka_cluster,
            ],
        )
        assert result.exit_code == 2

    @mock.patch("kfk.commands.users.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.users.replace_using_yaml")
    def test_add_topic_acl(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open("tests/files/yaml/user_with_authentication_tls.yaml") as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(
                kfk,
                [
                    "acls",
                    "--add",
                    "--topic",
                    self.topic,
                    "--allow-principal",
                    "User:" + self.user,
                    "--operation",
                    "Read",
                    "-n",
                    self.namespace,
                    "-c",
                    self.kafka_cluster,
                ],
            )
            assert result.exit_code == 0

            with open(
                "tests/files/yaml/user_with_authorization_with_one_topic_acl.yaml"
            ) as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_user_yaml == result_user_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.users.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.users.replace_using_yaml")
    def test_remove_topic_acl(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open(
            "tests/files/yaml/user_with_authorization_with_one_topic_acl.yaml"
        ) as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(
                kfk,
                [
                    "acls",
                    "--remove",
                    "--topic",
                    self.topic,
                    "--allow-principal",
                    "User:" + self.user,
                    "--operation",
                    "Read",
                    "-n",
                    self.namespace,
                    "-c",
                    self.kafka_cluster,
                ],
            )
            assert result.exit_code == 0

            with open("tests/files/yaml/user_with_authentication_tls.yaml") as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_user_yaml == result_user_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.users.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.users.replace_using_yaml")
    def test_add_topic_acl_to_one_acl(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open(
            "tests/files/yaml/user_with_authorization_with_one_topic_acl.yaml"
        ) as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(
                kfk,
                [
                    "acls",
                    "--add",
                    "--topic",
                    self.topic,
                    "--allow-principal",
                    "User:" + self.user,
                    "--operation",
                    "Write",
                    "-n",
                    self.namespace,
                    "-c",
                    self.kafka_cluster,
                ],
            )
            assert result.exit_code == 0

            with open(
                "tests/files/yaml/user_with_authorization_with_two_topic_acls.yaml"
            ) as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_user_yaml == result_user_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.users.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.users.replace_using_yaml")
    def test_remove_topic_acl_from_two_acls(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open(
            "tests/files/yaml/user_with_authorization_with_two_topic_acls.yaml"
        ) as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(
                kfk,
                [
                    "acls",
                    "--remove",
                    "--topic",
                    self.topic,
                    "--allow-principal",
                    "User:" + self.user,
                    "--operation",
                    "Write",
                    "-n",
                    self.namespace,
                    "-c",
                    self.kafka_cluster,
                ],
            )
            assert result.exit_code == 0

            with open(
                "tests/files/yaml/user_with_authorization_with_one_topic_acl.yaml"
            ) as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_user_yaml == result_user_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.users.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.users.replace_using_yaml")
    def test_add_topic_acl_with_two_operations(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open(
            "tests/files/yaml/user_with_authorization_with_one_topic_acl.yaml"
        ) as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(
                kfk,
                [
                    "acls",
                    "--add",
                    "--topic",
                    self.topic,
                    "--allow-principal",
                    "User:" + self.user,
                    "--operation",
                    "Write",
                    "--operation",
                    "Describe",
                    "-n",
                    self.namespace,
                    "-c",
                    self.kafka_cluster,
                ],
            )
            assert result.exit_code == 0

            with open(
                "tests/files/yaml/user_with_authorization_with_three_topic_acls.yaml"
            ) as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_user_yaml == result_user_yaml

        mock_replace_using_yaml.assert_called_once()

    @mock.patch("kfk.commands.users.create_temp_file")
    @mock.patch("kfk.commons.get_resource_yaml")
    @mock.patch("kfk.commands.users.replace_using_yaml")
    def test_add_group_acl(
        self, mock_replace_using_yaml, mock_get_resource_yaml, mock_create_temp_file
    ):
        with open(
            "tests/files/yaml/user_with_authorization_with_one_topic_acl.yaml"
        ) as file:
            user_yaml = file.read()
            mock_get_resource_yaml.return_value = user_yaml

            result = self.runner.invoke(
                kfk,
                [
                    "acls",
                    "--add",
                    "--group",
                    self.group,
                    "--allow-principal",
                    "User:" + self.user,
                    "--operation",
                    "Read",
                    "-n",
                    self.namespace,
                    "-c",
                    self.kafka_cluster,
                ],
            )
            assert result.exit_code == 0

            with open(
                "tests/files/yaml/user_with_authorization_"
                "with_one_topic_and_one_group_acls.yaml"
            ) as file:
                expected_user_yaml = file.read()
                result_user_yaml = mock_create_temp_file.call_args[0][0]
                assert expected_user_yaml == result_user_yaml

        mock_replace_using_yaml.assert_called_once()
