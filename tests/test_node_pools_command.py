from unittest import TestCase, mock

from click.testing import CliRunner

from kfk.commands.main import kfk


class TestKfkNodePools(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.cluster = "my-cluster"
        self.namespace = "kafka"
        self.node_pool = "my-pool"

    def test_no_option(self):
        result = self.runner.invoke(
            kfk,
            [
                "node-pools",
                "--node-pool",
                self.node_pool,
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

    @mock.patch("kfk.commands.node_pools.list_resource")
    def test_list_node_pools(self, mock_list_resource):
        result = self.runner.invoke(
            kfk,
            [
                "node-pools",
                "--list",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_list_resource.assert_called_with(
            "kafkanodepools",
            self.namespace,
            label=f"strimzi.io/cluster={self.cluster}",
        )

    @mock.patch("kfk.commands.node_pools.describe_resource")
    def test_describe_node_pool(self, mock_describe_resource):
        result = self.runner.invoke(
            kfk,
            [
                "node-pools",
                "--node-pool",
                self.node_pool,
                "--describe",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_describe_resource.assert_called_with(
            "kafkanodepools", self.node_pool, self.namespace
        )

    @mock.patch("kfk.commands.node_pools.get_resource")
    def test_describe_node_pool_output_yaml(self, mock_get_resource):
        mock_get_resource.return_value = {
            "apiVersion": "kafka.strimzi.io/v1beta2",
            "kind": "KafkaNodePool",
        }
        result = self.runner.invoke(
            kfk,
            [
                "node-pools",
                "--node-pool",
                self.node_pool,
                "--describe",
                "-o",
                "yaml",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_get_resource.assert_called_with(
            "kafkanodepools", self.node_pool, self.namespace
        )

    @mock.patch("kfk.commands.node_pools.get_resource")
    def test_describe_node_pool_output_json(self, mock_get_resource):
        mock_get_resource.return_value = {
            "apiVersion": "kafka.strimzi.io/v1beta2",
            "kind": "KafkaNodePool",
        }
        result = self.runner.invoke(
            kfk,
            [
                "node-pools",
                "--node-pool",
                self.node_pool,
                "--describe",
                "-o",
                "json",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

    @mock.patch("kfk.commons.create_temp_file")
    @mock.patch("kfk.commands.node_pools.create_using_yaml")
    def test_create_node_pool(self, mock_create_using_yaml, mock_create_temp_file):
        result = self.runner.invoke(
            kfk,
            [
                "node-pools",
                "--node-pool",
                self.node_pool,
                "--create",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_create_using_yaml.assert_called_once()

        result_yaml = mock_create_temp_file.call_args[0][0]
        assert "KafkaNodePool" in result_yaml
        assert self.node_pool in result_yaml
        assert self.cluster in result_yaml

    @mock.patch("kfk.commons.create_temp_file")
    @mock.patch("kfk.commands.node_pools.create_using_yaml")
    def test_create_node_pool_with_replicas(
        self, mock_create_using_yaml, mock_create_temp_file
    ):
        result = self.runner.invoke(
            kfk,
            [
                "node-pools",
                "--node-pool",
                self.node_pool,
                "--create",
                "--replicas",
                "5",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0

        result_yaml = mock_create_temp_file.call_args[0][0]
        assert "replicas: 5" in result_yaml

    @mock.patch("kfk.commons.create_temp_file")
    @mock.patch("kfk.commands.node_pools.delete_using_yaml")
    def test_delete_node_pool(self, mock_delete_using_yaml, mock_create_temp_file):
        result = self.runner.invoke(
            kfk,
            [
                "node-pools",
                "--node-pool",
                self.node_pool,
                "--delete",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        mock_delete_using_yaml.assert_called_once()

    def test_delete_default_broker_pool(self):
        result = self.runner.invoke(
            kfk,
            [
                "node-pools",
                "--node-pool",
                "broker",
                "--delete",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        assert "Cannot delete default node pool" in result.output

    def test_delete_default_controller_pool(self):
        result = self.runner.invoke(
            kfk,
            [
                "node-pools",
                "--node-pool",
                "controller",
                "--delete",
                "-c",
                self.cluster,
                "-n",
                self.namespace,
            ],
        )
        assert result.exit_code == 0
        assert "Cannot delete default node pool" in result.output
