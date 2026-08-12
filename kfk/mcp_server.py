from fastmcp import FastMCP

from kfk.commands import acls, clusters, node_pools, operator, topics, users
from kfk.commands.connect import clusters as connect_clusters
from kfk.commands.connect import connectors, mirror_maker
from kfk.commands.main import version as cli_version
from kfk.kubernetes_commons import get_resource

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

# Connect Clusters
mcp.tool(name="list_connects", description="List KafkaConnect clusters.")(
    connect_clusters.list
)
mcp.tool(name="get_connect", description="Get a KafkaConnect cluster resource.")(
    connect_clusters.describe
)
mcp.tool(name="create_connect", description="Create a KafkaConnect cluster.")(
    connect_clusters.create
)
mcp.tool(name="delete_connect", description="Delete a KafkaConnect cluster.")(
    connect_clusters.delete
)
mcp.tool(name="alter_connect", description="Alter a KafkaConnect cluster.")(
    connect_clusters.alter
)

# Connectors
mcp.tool(name="list_connectors", description="List KafkaConnectors.")(connectors.list)
mcp.tool(name="get_connector", description="Get a KafkaConnector resource.")(
    connectors.describe
)
mcp.tool(name="create_connector", description="Create a KafkaConnector.")(
    connectors.create
)
mcp.tool(name="delete_connector", description="Delete a KafkaConnector.")(
    connectors.delete
)
mcp.tool(name="alter_connector", description="Alter a KafkaConnector.")(
    connectors.alter
)

# ACLs
mcp.tool(name="add_or_remove_acls", description="Add or remove ACLs on Kafka.")(
    acls.add_or_remove
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


# MirrorMaker2
mcp.tool(
    name="list_mirror_maker_2s",
    description="List KafkaMirrorMaker2s in the namespace.",
)(mirror_maker.list)
mcp.tool(
    name="get_mirror_maker_2",
    description="Describe a KafkaMirrorMaker2 resource.",
)(mirror_maker.describe)
mcp.tool(
    name="create_mirror_maker_2",
    description="Create a KafkaMirrorMaker2 resource.",
)(mirror_maker.create)
mcp.tool(
    name="delete_mirror_maker_2",
    description="Delete a KafkaMirrorMaker2 resource.",
)(mirror_maker.delete)

# Node Pools
mcp.tool(name="list_node_pools", description="List KafkaNodePools in the namespace.")(
    node_pools.list
)
mcp.tool(name="get_node_pool", description="Describe a KafkaNodePool resource.")(
    node_pools.describe
)
mcp.tool(name="create_node_pool", description="Create a KafkaNodePool resource.")(
    node_pools.create
)
mcp.tool(name="delete_node_pool", description="Delete a KafkaNodePool resource.")(
    node_pools.delete
)


# Backup
@mcp.tool()
def backup_kafka(
    cluster: str, namespace: str, output: str = "", include_secrets: bool = False
) -> str:
    """Back up a Kafka cluster and its resources to a gzip archive."""
    from kfk.commands.backup.commons import (
        clean_metadata,
        clean_secret_metadata,
        create_archive,
        get_custom_resources,
        get_secrets,
    )

    if not output:
        output = f"{cluster}-backup.tar.gz"
    resources = {}
    kafkas = get_custom_resources("kafkas", namespace)
    for k in kafkas:
        if k["metadata"]["name"] == cluster:
            resources["kafka.yaml"] = clean_metadata(k)
            break
    else:
        return f"Kafka cluster '{cluster}' not found in namespace '{namespace}'"
    for np in get_custom_resources(
        "kafkanodepools", namespace, label=f"strimzi.io/cluster={cluster}"
    ):
        name = np["metadata"]["name"]
        resources[f"nodepools/{name}.yaml"] = clean_metadata(np)
    for topic in get_custom_resources(
        "kafkatopics", namespace, label=f"strimzi.io/cluster={cluster}"
    ):
        name = topic["metadata"]["name"]
        resources[f"topics/{name}.yaml"] = clean_metadata(topic)
    users = get_custom_resources(
        "kafkausers", namespace, label=f"strimzi.io/cluster={cluster}"
    )
    for user in users:
        name = user["metadata"]["name"]
        resources[f"users/{name}.yaml"] = clean_metadata(user)
    if include_secrets:
        for secret in get_secrets(
            namespace,
            f"strimzi.io/cluster={cluster},strimzi.io/kind=Kafka",
        ):
            name = secret["metadata"]["name"]
            resources[f"secrets/{name}.yaml"] = clean_secret_metadata(secret)
        for user in users:
            user_name = user["metadata"]["name"]
            label = (
                f"strimzi.io/cluster={cluster},"
                f"strimzi.io/kind=KafkaUser,"
                f"strimzi.io/name={user_name}"
            )
            for secret in get_secrets(namespace, label):
                name = secret["metadata"]["name"]
                resources[f"secrets/{name}.yaml"] = clean_secret_metadata(secret)
    create_archive(resources, output)
    return f"Backup saved to {output} ({len(resources)} resources)"


@mcp.tool()
def restore_kafka(from_backup: str, cluster: str, namespace: str) -> str:
    """Restore a Kafka cluster and its resources from a backup archive."""
    from kfk.commands.backup.commons import (
        extract_archive,
        restore_custom_resource,
        restore_secret,
    )

    resources = extract_archive(from_backup)
    restored = []
    if "kafka.yaml" in resources:
        resource = resources["kafka.yaml"]
        resource["metadata"]["name"] = cluster
        restore_custom_resource(resource, namespace)
        restored.append(f"Kafka/{cluster}")
    for name, resource in sorted(resources.items()):
        if name.startswith("nodepools/"):
            restore_custom_resource(resource, namespace)
            restored.append(name)
    for name, resource in sorted(resources.items()):
        if name.startswith("topics/"):
            restore_custom_resource(resource, namespace)
            restored.append(name)
    for name, resource in sorted(resources.items()):
        if name.startswith("users/"):
            restore_custom_resource(resource, namespace)
            restored.append(name)
    for name, resource in sorted(resources.items()):
        if name.startswith("secrets/"):
            restore_secret(resource, namespace)
            restored.append(name)
    return f"Restored {len(restored)} resources to namespace '{namespace}'"


@mcp.tool()
def backup_connect(cluster: str, namespace: str, output: str = "") -> str:
    """Back up a Kafka Connect cluster and its connectors to a gzip archive."""
    from kfk.commands.backup.commons import (
        clean_metadata,
        create_archive,
        get_custom_resources,
    )

    if not output:
        output = f"{cluster}-connect-backup.tar.gz"
    resources = {}
    connects = get_custom_resources("kafkaconnects", namespace)
    for kc in connects:
        if kc["metadata"]["name"] == cluster:
            resources["connect.yaml"] = clean_metadata(kc)
            break
    else:
        return f"KafkaConnect '{cluster}' not found in namespace '{namespace}'"
    for connector in get_custom_resources(
        "kafkaconnectors",
        namespace,
        label=f"strimzi.io/cluster={cluster}",
    ):
        name = connector["metadata"]["name"]
        resources[f"connectors/{name}.yaml"] = clean_metadata(connector)
    create_archive(resources, output)
    return f"Backup saved to {output} ({len(resources)} resources)"


@mcp.tool()
def restore_connect(from_backup: str, cluster: str, namespace: str) -> str:
    """Restore a Kafka Connect cluster and its connectors from a backup archive."""
    from kfk.commands.backup.commons import extract_archive, restore_custom_resource

    resources = extract_archive(from_backup)
    restored = []
    if "connect.yaml" in resources:
        resource = resources["connect.yaml"]
        resource["metadata"]["name"] = cluster
        restore_custom_resource(resource, namespace)
        restored.append(f"KafkaConnect/{cluster}")
    for name, resource in sorted(resources.items()):
        if name.startswith("connectors/"):
            restore_custom_resource(resource, namespace)
            restored.append(name)
    return f"Restored {len(restored)} resources to namespace '{namespace}'"


# Version
@mcp.tool()
def get_version() -> str:
    """Get Strimzi CLI and Strimzi version information."""
    return cli_version
