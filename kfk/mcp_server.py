from fastmcp import FastMCP

from kfk.commands import acls, clusters, node_pools, operator, topics, users
from kfk.commands.connect import clusters as connect_clusters
from kfk.commands.connect import connectors, mirror_maker
from kfk.commands.main import version as cli_version
from kfk.kubernetes_commons import get_resource

mcp = FastMCP("strimzi-kafka-cli")


def _to_tuple(value) -> tuple:
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return (value,)


# Kafka Clusters


@mcp.tool()
def list_kafkas(namespace: str) -> str:
    """List all Kafka clusters in the namespace."""
    return clusters.list(namespace)


@mcp.tool()
def get_kafka(cluster: str, namespace: str, output: str = "yaml") -> str:
    """Get a Kafka cluster resource."""
    return clusters.describe(cluster, output, namespace)


@mcp.tool()
def create_kafka(
    cluster: str,
    namespace: str,
    replicas: int = None,
    config: list[str] = None,
    add_listener: list[str] = None,
    listener_auth: str = None,
) -> str:
    """Create a Kafka cluster from template."""
    return clusters.create(
        cluster,
        replicas,
        _to_tuple(config),
        _to_tuple(add_listener),
        listener_auth,
        namespace,
        is_yes=True,
    )


@mcp.tool()
def delete_kafka(cluster: str, namespace: str) -> str:
    """Delete a Kafka cluster."""
    return clusters.delete(cluster, namespace, is_yes=True)


@mcp.tool()
def alter_kafka_config(
    cluster: str,
    namespace: str,
    replicas: int = None,
    config: list[str] = None,
    delete_config: list[str] = None,
    add_listener: list[str] = None,
    listener_auth: str = None,
    listener_auth_config: list[str] = None,
    delete_listener: list[str] = None,
    authorization_type: str = None,
    super_user: list[str] = None,
    authorizer_class: str = None,
) -> str:
    """Alter cluster-level Kafka configuration."""
    return clusters.alter(
        cluster,
        replicas,
        _to_tuple(config),
        _to_tuple(delete_config),
        _to_tuple(add_listener),
        listener_auth,
        _to_tuple(listener_auth_config),
        _to_tuple(delete_listener),
        authorization_type,
        _to_tuple(super_user),
        authorizer_class,
        namespace,
    )


@mcp.tool()
def get_kafka_status(cluster: str, namespace: str) -> dict:
    """Get the status and conditions of a Kafka cluster."""
    resource = get_resource("kafkas", cluster, namespace)
    return resource.get("status", {})


# Topics


@mcp.tool()
def list_topics(cluster: str, namespace: str) -> str:
    """List Kafka topics in the specified cluster."""
    return topics.list(cluster, namespace)


@mcp.tool()
def get_topic(topic: str, cluster: str, namespace: str, output: str = "yaml") -> str:
    """Get a Kafka topic resource."""
    return topics.describe(topic, output, False, None, cluster, namespace)


@mcp.tool()
def create_topic(
    topic: str,
    cluster: str,
    namespace: str,
    partitions: int = 1,
    replication_factor: int = 1,
    config: list[str] = None,
) -> str:
    """Create a Kafka topic."""
    return topics.create(
        topic, partitions, replication_factor, _to_tuple(config), cluster, namespace
    )


@mcp.tool()
def delete_topic(topic: str, cluster: str, namespace: str) -> str:
    """Delete a Kafka topic."""
    return topics.delete(topic, cluster, namespace)


@mcp.tool()
def alter_topic(
    topic: str,
    cluster: str,
    namespace: str,
    partitions: int = None,
    replication_factor: int = None,
    config: list[str] = None,
    delete_config: list[str] = None,
) -> str:
    """Alter a Kafka topic."""
    return topics.alter(
        topic,
        partitions,
        replication_factor,
        _to_tuple(config),
        _to_tuple(delete_config),
        cluster,
        namespace,
    )


# Users


@mcp.tool()
def list_users(cluster: str, namespace: str) -> str:
    """List Kafka users in the specified cluster."""
    return users.list(cluster, namespace)


@mcp.tool()
def get_user(user: str, cluster: str, namespace: str, output: str = "yaml") -> str:
    """Get a Kafka user resource."""
    return users.describe(user, output, cluster, namespace)


@mcp.tool()
def create_user(
    user: str,
    cluster: str,
    namespace: str,
    authentication_type: str = "tls",
    quota: list[str] = None,
) -> str:
    """Create a Kafka user."""
    return users.create(user, authentication_type, _to_tuple(quota), cluster, namespace)


@mcp.tool()
def delete_user(user: str, cluster: str, namespace: str) -> str:
    """Delete a Kafka user."""
    return users.delete(user, cluster, namespace)


@mcp.tool()
def alter_user(
    user: str,
    cluster: str,
    namespace: str,
    authentication_type: str = None,
    authorization_type: str = None,
    add_acl: bool = False,
    delete_acl: bool = False,
    operation: list[str] = None,
    host: str = None,
    acl_type: str = None,
    resource_type: str = None,
    resource_name: str = None,
    resource_pattern_type: str = None,
    quota: list[str] = None,
    delete_quota: list[str] = None,
) -> str:
    """Alter a Kafka user."""
    return users.alter(
        user,
        authentication_type,
        authorization_type,
        add_acl,
        delete_acl,
        _to_tuple(operation),
        host,
        acl_type,
        resource_type,
        resource_name,
        resource_pattern_type,
        _to_tuple(quota),
        _to_tuple(delete_quota),
        cluster,
        namespace,
    )


# Connect Clusters


@mcp.tool()
def list_connects(namespace: str) -> str:
    """List KafkaConnect clusters."""
    return connect_clusters.list(namespace)


@mcp.tool()
def get_connect(cluster: str, namespace: str, output: str = "yaml") -> str:
    """Get a KafkaConnect cluster resource."""
    return connect_clusters.describe(cluster, output, namespace)


@mcp.tool()
def create_connect(
    cluster: str,
    config_file: str,
    namespace: str,
    replicas: int = None,
    registry_username: str = None,
    registry_password: str = None,
    connector_config_files: list[str] = None,
) -> str:
    """Create a KafkaConnect cluster."""
    return connect_clusters.create(
        cluster,
        replicas,
        registry_username,
        registry_password,
        config_file,
        _to_tuple(connector_config_files),
        namespace,
        is_yes=True,
    )


@mcp.tool()
def delete_connect(cluster: str, namespace: str) -> str:
    """Delete a KafkaConnect cluster."""
    return connect_clusters.delete(cluster, namespace, is_yes=True)


@mcp.tool()
def alter_connect(
    cluster: str,
    namespace: str,
    replicas: int = None,
    config_file: str = None,
) -> str:
    """Alter a KafkaConnect cluster."""
    return connect_clusters.alter(cluster, replicas, config_file, namespace)


# Connectors


@mcp.tool()
def list_connectors(cluster: str, namespace: str) -> str:
    """List KafkaConnectors."""
    return connectors.list(cluster, namespace)


@mcp.tool()
def get_connector(connector: str, namespace: str, output: str = "yaml") -> str:
    """Get a KafkaConnector resource."""
    return connectors.describe(connector, output, namespace)


@mcp.tool()
def create_connector(config_file: str, cluster: str, namespace: str) -> str:
    """Create a KafkaConnector."""
    return connectors.create(config_file, cluster, namespace)


@mcp.tool()
def delete_connector(connector: str, cluster: str, namespace: str) -> str:
    """Delete a KafkaConnector."""
    return connectors.delete(connector, cluster, namespace)


@mcp.tool()
def alter_connector(config_file: str, cluster: str, namespace: str) -> str:
    """Alter a KafkaConnector."""
    return connectors.alter(config_file, cluster, namespace)


# ACLs


@mcp.tool()
def add_or_remove_acls(
    kafka_cluster: str,
    namespace: str,
    add: bool = False,
    remove: bool = False,
    allow_principal: str = None,
    deny_principal: str = None,
    operation: list[str] = None,
    allow_host: str = None,
    deny_host: str = None,
    resource_pattern_type: str = None,
    topic: str = None,
    cluster: str = None,
    group: str = None,
) -> str:
    """Add or remove ACLs on Kafka."""
    return acls.add_or_remove(
        topic,
        cluster,
        group,
        add,
        remove,
        allow_principal,
        deny_principal,
        _to_tuple(operation),
        allow_host,
        deny_host,
        resource_pattern_type,
        kafka_cluster,
        namespace,
    )


# Operator


@mcp.tool()
def install_operator(namespace: str) -> str:
    """Install the Strimzi Kafka Operator."""
    return operator.install(namespace)


@mcp.tool()
def uninstall_operator(namespace: str) -> str:
    """Uninstall the Strimzi Kafka Operator."""
    return operator.uninstall(namespace)


# MirrorMaker2


@mcp.tool()
def list_mirror_maker_2s(namespace: str) -> str:
    """List KafkaMirrorMaker2s in the namespace."""
    return mirror_maker.list(namespace)


@mcp.tool()
def get_mirror_maker_2(
    mirror_maker_name: str, namespace: str, output: str = "yaml"
) -> str:
    """Describe a KafkaMirrorMaker2 resource."""
    return mirror_maker.describe(mirror_maker_name, output, namespace)


@mcp.tool()
def create_mirror_maker_2(
    mirror_maker_name: str,
    config_file: str,
    namespace: str,
    replicas: int = 1,
) -> str:
    """Create a KafkaMirrorMaker2 resource."""
    return mirror_maker.create(mirror_maker_name, config_file, replicas, namespace)


@mcp.tool()
def delete_mirror_maker_2(mirror_maker_name: str, namespace: str) -> str:
    """Delete a KafkaMirrorMaker2 resource."""
    return mirror_maker.delete(mirror_maker_name, namespace)


# Node Pools


@mcp.tool()
def list_node_pools(cluster: str, namespace: str) -> str:
    """List KafkaNodePools in the namespace."""
    return node_pools.list(cluster, namespace)


@mcp.tool()
def get_node_pool(
    node_pool: str, cluster: str, namespace: str, output: str = "yaml"
) -> str:
    """Describe a KafkaNodePool resource."""
    return node_pools.describe(node_pool, output, cluster, namespace)


@mcp.tool()
def create_node_pool(
    node_pool: str, cluster: str, namespace: str, replicas: int = None
) -> str:
    """Create a KafkaNodePool resource."""
    return node_pools.create(node_pool, replicas, cluster, namespace)


@mcp.tool()
def delete_node_pool(node_pool: str, cluster: str, namespace: str) -> str:
    """Delete a KafkaNodePool resource."""
    return node_pools.delete(node_pool, cluster, namespace)


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
    backup_users = get_custom_resources(
        "kafkausers", namespace, label=f"strimzi.io/cluster={cluster}"
    )
    for user in backup_users:
        name = user["metadata"]["name"]
        resources[f"users/{name}.yaml"] = clean_metadata(user)
    if include_secrets:
        for secret in get_secrets(
            namespace,
            f"strimzi.io/cluster={cluster},strimzi.io/kind=Kafka",
        ):
            name = secret["metadata"]["name"]
            resources[f"secrets/{name}.yaml"] = clean_secret_metadata(secret)
        for user in backup_users:
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
