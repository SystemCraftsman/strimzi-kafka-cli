from fastmcp import FastMCP

from kfk.commands import clusters, operator, topics, users
from kfk.commands.connect import clusters as connect_clusters
from kfk.commands.connect import connectors
from kfk.commands.main import version as cli_version
from kfk.kubernetes_commons import get_resource, list_resource

mcp = FastMCP("strimzi-kafka-cli")

# Kafka Clusters
mcp.tool(name="list_kafkas", description="List all Kafka clusters in the namespace.")(
    clusters.list
)
mcp.tool(name="get_kafka", description="Get a Kafka cluster resource.")(
    clusters.describe
)
mcp.tool(name="create_kafka", description="Create a Kafka cluster from template.")(
    clusters.create
)
mcp.tool(name="delete_kafka", description="Delete a Kafka cluster.")(clusters.delete)
mcp.tool(
    name="alter_kafka_config",
    description="Alter cluster-level Kafka configuration.",
)(clusters.alter)


@mcp.tool()
def get_kafka_status(cluster: str, namespace: str) -> dict:
    """Get the status and conditions of a Kafka cluster."""
    resource = get_resource("kafkas", cluster, namespace)
    return resource.get("status", {})


# Topics
mcp.tool(name="list_topics", description="List Kafka topics in the specified cluster.")(
    topics.list
)
mcp.tool(name="get_topic", description="Get a Kafka topic resource.")(topics.describe)
mcp.tool(name="create_topic", description="Create a Kafka topic.")(topics.create)
mcp.tool(name="delete_topic", description="Delete a Kafka topic.")(topics.delete)
mcp.tool(name="alter_topic", description="Alter a Kafka topic.")(topics.alter)

# Users
mcp.tool(name="list_users", description="List Kafka users in the specified cluster.")(
    users.list
)
mcp.tool(name="get_user", description="Get a Kafka user resource.")(users.describe)
mcp.tool(name="create_user", description="Create a Kafka user.")(users.create)
mcp.tool(name="delete_user", description="Delete a Kafka user.")(users.delete)
mcp.tool(name="alter_user", description="Alter a Kafka user.")(users.alter)

# Connect
mcp.tool(name="list_connects", description="List KafkaConnect clusters.")(
    connect_clusters.list
)
mcp.tool(name="get_connect", description="Get a KafkaConnect cluster resource.")(
    connect_clusters.describe
)
mcp.tool(name="list_connectors", description="List KafkaConnectors.")(connectors.list)
mcp.tool(name="get_connector", description="Get a KafkaConnector resource.")(
    connectors.describe
)


# Operator
mcp.tool(
    name="install_operator",
    description="Install the Strimzi Kafka Operator.",
)(operator.install)
mcp.tool(
    name="uninstall_operator",
    description="Uninstall the Strimzi Kafka Operator.",
)(operator.uninstall)


# Node Pools
@mcp.tool()
def list_node_pools(namespace: str) -> dict:
    """List KafkaNodePools in the namespace."""
    return list_resource("kafkanodepools", namespace)


@mcp.tool()
def get_node_pool(pool: str, namespace: str) -> dict:
    """Get a KafkaNodePool resource."""
    return get_resource("kafkanodepools", pool, namespace)


# Version
@mcp.tool()
def get_version() -> str:
    """Get Strimzi CLI and Strimzi version information."""
    return cli_version
