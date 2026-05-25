import asyncio
from unittest import TestCase, mock

from kfk.config import STRIMZI_VERSION


@mock.patch("kfk.kubernetes_commons.config.load_kube_config")
@mock.patch("kfk.kubernetes_commons._detect_strimzi_api_version", return_value="v1")
class TestMcpServer(TestCase):
    def test_tools_registered(self, mock_detect, mock_kube):
        from kfk.mcp_server import mcp

        tools = asyncio.run(mcp.list_tools())
        tool_names = [t.name for t in tools]
        expected_tools = [
            "list_kafkas",
            "get_kafka",
            "create_kafka",
            "delete_kafka",
            "alter_kafka_config",
            "get_kafka_status",
            "list_topics",
            "get_topic",
            "create_topic",
            "delete_topic",
            "alter_topic",
            "list_users",
            "get_user",
            "create_user",
            "delete_user",
            "alter_user",
            "list_connects",
            "get_connect",
            "list_connectors",
            "get_connector",
            "list_node_pools",
            "get_node_pool",
            "get_version",
        ]
        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Tool '{tool_name}' not registered"

    def test_get_version(self, mock_detect, mock_kube):
        from kfk.mcp_server import get_version

        result = get_version()
        assert f"Strimzi Version: {STRIMZI_VERSION}" in result
        assert "CLI Version:" in result
