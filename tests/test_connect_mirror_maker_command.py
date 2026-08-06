from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.commands.connect.mirror_maker import connect


class TestKfkConnectMirrorMaker(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.namespace = "kafka"
        self.mirror_maker = "my-mm2"
        self.config_file = "tests/files/mm2.properties"

    def test_no_option(self):
        result = self.runner.invoke(
            connect,
            ["mirror-maker", "--mirror-maker", self.mirror_maker, "-n", self.namespace],
        )
        assert result.exit_code == 0

    @mock.patch("kfk.commands.connect.mirror_maker.list_resource")
    def test_list_mirror_makers(self, mock_list_resource):
        result = self.runner.invoke(
            connect,
            ["mirror-maker", "--list", "-n", self.namespace],
        )
        assert result.exit_code == 0
        mock_list_resource.assert_called_with("kafkamirrormaker2s", self.namespace)

    @mock.patch("kfk.commands.connect.mirror_maker.describe_resource")
    def test_describe_mirror_maker(self, mock_describe_resource):
        result = self.runner.invoke(
            connect,
            [
                "mirror-maker",
                "--mirror-maker",
                self.mirror_maker,
                "--describe",
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_describe_resource.assert_called_with(
            "kafkamirrormaker2s", self.mirror_maker, self.namespace
        )

    @mock.patch("kfk.commands.connect.mirror_maker.get_resource")
    def test_describe_mirror_maker_output_yaml(self, mock_get_resource):
        mock_get_resource.return_value = {
            "apiVersion": "kafka.strimzi.io/v1beta2",
            "kind": "KafkaMirrorMaker2",
        }
        result = self.runner.invoke(
            connect,
            [
                "mirror-maker",
                "--mirror-maker",
                self.mirror_maker,
                "--describe",
                "-o",
                "yaml",
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_get_resource.assert_called_with(
            "kafkamirrormaker2s", self.mirror_maker, self.namespace
        )

    @mock.patch("kfk.commands.connect.mirror_maker.get_resource")
    def test_describe_mirror_maker_output_json(self, mock_get_resource):
        mock_get_resource.return_value = {
            "apiVersion": "kafka.strimzi.io/v1beta2",
            "kind": "KafkaMirrorMaker2",
        }
        result = self.runner.invoke(
            connect,
            [
                "mirror-maker",
                "--mirror-maker",
                self.mirror_maker,
                "--describe",
                "-o",
                "json",
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

    @mock.patch("kfk.commands.connect.mirror_maker.create_temp_file")
    @mock.patch("kfk.commands.connect.mirror_maker.create_using_yaml")
    def test_create_mirror_maker(self, mock_create_using_yaml, mock_create_temp_file):
        result = self.runner.invoke(
            connect,
            [
                "mirror-maker",
                "--mirror-maker",
                self.mirror_maker,
                "--create",
                "--config",
                self.config_file,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_create_using_yaml.assert_called_once()

        result_yaml = mock_create_temp_file.call_args[0][0]
        assert "KafkaMirrorMaker2" in result_yaml
        assert self.mirror_maker in result_yaml
        assert "source-kafka:9092" in result_yaml
        assert "target-kafka:9092" in result_yaml
        assert "tasksMax: 4" in result_yaml

    @mock.patch("kfk.commands.connect.mirror_maker.create_temp_file")
    @mock.patch("kfk.commands.connect.mirror_maker.create_using_yaml")
    def test_create_mirror_maker_with_replicas(
        self, mock_create_using_yaml, mock_create_temp_file
    ):
        result = self.runner.invoke(
            connect,
            [
                "mirror-maker",
                "--mirror-maker",
                self.mirror_maker,
                "--create",
                "--config",
                self.config_file,
                "--replicas",
                "3",
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        result_yaml = mock_create_temp_file.call_args[0][0]
        assert "replicas: 3" in result_yaml

    def test_create_mirror_maker_without_config(self):
        result = self.runner.invoke(
            connect,
            [
                "mirror-maker",
                "--mirror-maker",
                self.mirror_maker,
                "--create",
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code != 0

    @mock.patch("kfk.commands.connect.mirror_maker.create_temp_file")
    @mock.patch("kfk.commands.connect.mirror_maker.delete_using_yaml")
    def test_delete_mirror_maker(self, mock_delete_using_yaml, mock_create_temp_file):
        result = self.runner.invoke(
            connect,
            [
                "mirror-maker",
                "--mirror-maker",
                self.mirror_maker,
                "--delete",
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_delete_using_yaml.assert_called_once()

        result_yaml = mock_create_temp_file.call_args[0][0]
        assert "KafkaMirrorMaker2" in result_yaml
        assert self.mirror_maker in result_yaml

    @mock.patch("kfk.commands.connect.mirror_maker.create_temp_file")
    @mock.patch("kfk.commands.connect.mirror_maker.create_using_yaml")
    def test_create_mirror_maker_replication_factor(
        self, mock_create_using_yaml, mock_create_temp_file
    ):
        result = self.runner.invoke(
            connect,
            [
                "mirror-maker",
                "--mirror-maker",
                self.mirror_maker,
                "--create",
                "--config",
                self.config_file,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        result_yaml = mock_create_temp_file.call_args[0][0]
        assert "replication.factor" in result_yaml

    @mock.patch("kfk.commands.connect.mirror_maker.create_temp_file")
    @mock.patch("kfk.commands.connect.mirror_maker.create_using_yaml")
    def test_create_mirror_maker_minimal_config(
        self, mock_create_using_yaml, mock_create_temp_file
    ):
        result = self.runner.invoke(
            connect,
            [
                "mirror-maker",
                "--mirror-maker",
                self.mirror_maker,
                "--create",
                "--config",
                "tests/files/mm2_minimal.properties",
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        result_yaml = mock_create_temp_file.call_args[0][0]
        assert "tasksMax: 2" in result_yaml
        assert "topicsPattern: '*.'" in result_yaml or "topicsPattern" in result_yaml

    @mock.patch("kfk.commands.connect.mirror_maker.create_temp_file")
    @mock.patch("kfk.commands.connect.mirror_maker.create_using_yaml")
    def test_create_mirror_maker_with_cluster_config(
        self, mock_create_using_yaml, mock_create_temp_file
    ):
        result = self.runner.invoke(
            connect,
            [
                "mirror-maker",
                "--mirror-maker",
                self.mirror_maker,
                "--create",
                "--config",
                "tests/files/mm2_with_cluster_config.properties",
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        result_yaml = mock_create_temp_file.call_args[0][0]
        assert "ssl.truststore.location" in result_yaml
        assert "orders.*" in result_yaml
        assert "my-group.*" in result_yaml

    @mock.patch("kfk.commands.connect.mirror_maker.create_temp_file")
    @mock.patch("kfk.commands.connect.mirror_maker.create_using_yaml")
    def test_create_mirror_maker_default_replicas(
        self, mock_create_using_yaml, mock_create_temp_file
    ):
        result = self.runner.invoke(
            connect,
            [
                "mirror-maker",
                "--mirror-maker",
                self.mirror_maker,
                "--create",
                "--config",
                self.config_file,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        result_yaml = mock_create_temp_file.call_args[0][0]
        assert "replicas: 1" in result_yaml
