import json

import click
import yaml

from kfk.commands.connect import connect
from kfk.commons import create_temp_file, get_properties_from_file
from kfk.kubernetes_commons import (
    create_using_yaml,
    delete_using_yaml,
    describe_resource,
    get_resource,
    list_resource,
)
from kfk.option_extensions import NotRequiredIf

CLUSTER_KEYS = ("bootstrap.servers",)
GLOBAL_SKIP_KEYS = ("clusters", "tasks.max", "replication.factor")


def _is_cluster_key(key, cluster_aliases):
    for alias in cluster_aliases:
        if key.startswith(f"{alias}."):
            return True
    return False


def _is_mirror_key(key):
    return "->" in key


@click.option("-n", "--namespace", help="Namespace to use", required=True)
@click.option(
    "-o",
    "--output",
    help=(
        "Output format. One of:"
        " json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath"
        "|jsonpath-file."
    ),
)
@click.option(
    "--delete",
    "is_delete",
    help="Delete a KafkaMirrorMaker2.",
    is_flag=True,
)
@click.option(
    "--create",
    "is_create",
    help="Create a KafkaMirrorMaker2.",
    is_flag=True,
)
@click.option(
    "--describe",
    "is_describe",
    help="Describe a KafkaMirrorMaker2.",
    is_flag=True,
)
@click.option("--list", "is_list", help="List KafkaMirrorMaker2s.", is_flag=True)
@click.option(
    "--replicas",
    help="Number of MM2 Connect worker replicas.",
    type=int,
    default=1,
)
@click.option(
    "--config",
    "config_file",
    help="MM2 properties config file (connect-mirror-maker.sh format).",
    type=click.File("r"),
)
@click.option(
    "--mirror-maker",
    help="KafkaMirrorMaker2 name",
    required=True,
    cls=NotRequiredIf,
    options=["is_list"],
)
@connect.command(name="mirror-maker")
def mirror_maker(
    mirror_maker,
    config_file,
    replicas,
    is_list,
    is_describe,
    is_create,
    is_delete,
    output,
    namespace,
):
    """Lists, describes, creates, deletes KafkaMirrorMaker2(s)."""
    if is_list:
        list(namespace)
    elif is_describe:
        describe(mirror_maker, output, namespace)
    elif is_create:
        create(mirror_maker, config_file, replicas, namespace)
    elif is_delete:
        delete(mirror_maker, namespace)


def list(namespace):
    return list_resource("kafkamirrormaker2s", namespace)


def describe(mirror_maker, output, namespace):
    if output is not None:
        resource = get_resource("kafkamirrormaker2s", mirror_maker, namespace)
        if output == "yaml":
            click.echo(yaml.dump(resource, default_flow_style=False))
        elif output == "json":
            click.echo(json.dumps(resource, indent=2))
    else:
        describe_resource("kafkamirrormaker2s", mirror_maker, namespace)


def create(mirror_maker, config_file, replicas, namespace):
    properties = get_properties_from_file(config_file)

    clusters_str = properties.get("clusters")
    cluster_aliases = [c.strip() for c in clusters_str.data.split(",")]

    clusters = []
    for alias in cluster_aliases:
        bootstrap = properties.get(f"{alias}.bootstrap.servers")
        cluster_entry = {
            "alias": alias,
            "bootstrapServers": bootstrap.data,
        }
        cluster_config = {}
        for key in properties:
            if not key.startswith(f"{alias}."):
                continue
            suffix = key[len(f"{alias}.") :]
            if suffix in CLUSTER_KEYS:
                continue
            cluster_config[suffix] = properties.get(key).data
        if cluster_config:
            cluster_entry["config"] = cluster_config
        clusters.append(cluster_entry)

    mirrors = []
    for alias in cluster_aliases:
        for target_alias in cluster_aliases:
            if alias == target_alias:
                continue
            prefix = f"{alias}->{target_alias}"
            enabled = properties.get(f"{prefix}.enabled")
            if enabled is not None and enabled.data.lower() == "true":
                topics = properties.get(f"{prefix}.topics")
                groups = properties.get(f"{prefix}.groups")
                tasks_max_prop = properties.get("tasks.max")
                tasks_max = int(tasks_max_prop.data) if tasks_max_prop else 2
                mirror = {
                    "sourceCluster": alias,
                    "targetCluster": target_alias,
                    "sourceConnector": {"tasksMax": tasks_max},
                    "topicsPattern": topics.data if topics else ".*",
                    "groupsPattern": groups.data if groups else ".*",
                }
                mirrors.append(mirror)

    connect_cluster = cluster_aliases[-1] if cluster_aliases else "target"

    spec = {
        "version": "4.2.0",
        "replicas": replicas,
        "connectCluster": connect_cluster,
        "clusters": clusters,
        "mirrors": mirrors,
    }

    replication_factor = properties.get("replication.factor")
    if replication_factor:
        for mirror in spec["mirrors"]:
            mirror["sourceConnector"].setdefault("config", {})["replication.factor"] = (
                replication_factor.data
            )

    global_config = {}
    for key in properties:
        if key in GLOBAL_SKIP_KEYS:
            continue
        if _is_cluster_key(key, cluster_aliases):
            continue
        if _is_mirror_key(key):
            continue
        global_config[key] = properties.get(key).data
    if global_config:
        spec["config"] = global_config

    mm2_dict = {
        "apiVersion": "kafka.strimzi.io/v1beta2",
        "kind": "KafkaMirrorMaker2",
        "metadata": {"name": mirror_maker},
        "spec": spec,
    }

    mm2_yaml = yaml.dump(mm2_dict)
    temp_file = create_temp_file(mm2_yaml)
    create_using_yaml(temp_file.name, namespace)
    temp_file.close()


def delete(mirror_maker, namespace):
    mm2_dict = {
        "apiVersion": "kafka.strimzi.io/v1beta2",
        "kind": "KafkaMirrorMaker2",
        "metadata": {"name": mirror_maker, "namespace": namespace},
    }

    mm2_yaml = yaml.dump(mm2_dict)
    temp_file = create_temp_file(mm2_yaml)
    delete_using_yaml(temp_file.name, namespace)
    temp_file.close()
