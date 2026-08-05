import json

import click
import yaml

from kfk.commands.main import kfk
from kfk.kubernetes_commons import (
    create_using_yaml,
    delete_using_yaml,
    describe_resource,
    get_resource,
    list_resource,
)
from kfk.option_extensions import NotRequiredIf

DEFAULT_NODE_POOLS = ("broker", "controller")


@click.option("-n", "--namespace", help="Namespace to use", required=True)
@click.option("-c", "--cluster", help="Cluster to use", required=True)
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
    help="Delete a KafkaNodePool.",
    is_flag=True,
)
@click.option(
    "--create",
    "is_create",
    help="Create a KafkaNodePool.",
    is_flag=True,
)
@click.option(
    "--describe",
    "is_describe",
    help="Describe a KafkaNodePool.",
    is_flag=True,
)
@click.option("--list", "is_list", help="List KafkaNodePools.", is_flag=True)
@click.option(
    "--replicas",
    help="Number of replicas for the node pool.",
    type=int,
)
@click.option(
    "--node-pool",
    help="KafkaNodePool name",
    required=True,
    cls=NotRequiredIf,
    options=["is_list"],
)
@kfk.command(name="node-pools")
def node_pools(
    node_pool,
    replicas,
    is_list,
    is_describe,
    is_create,
    is_delete,
    output,
    cluster,
    namespace,
):
    """Lists, describes, creates, deletes KafkaNodePool(s)."""
    if is_list:
        list(cluster, namespace)
    elif is_describe:
        describe(node_pool, output, cluster, namespace)
    elif is_create:
        create(node_pool, replicas, cluster, namespace)
    elif is_delete:
        delete(node_pool, cluster, namespace)


def list(cluster, namespace):
    return list_resource(
        "kafkanodepools", namespace, label=f"strimzi.io/cluster={cluster}"
    )


def describe(node_pool, output, cluster, namespace):
    if output is not None:
        resource = get_resource("kafkanodepools", node_pool, namespace)
        if output == "yaml":
            click.echo(yaml.dump(resource, default_flow_style=False))
        elif output == "json":
            click.echo(json.dumps(resource, indent=2))
    else:
        describe_resource("kafkanodepools", node_pool, namespace)


def create(node_pool, replicas, cluster, namespace):
    node_pool_dict = {
        "apiVersion": "kafka.strimzi.io/v1beta2",
        "kind": "KafkaNodePool",
        "metadata": {
            "name": node_pool,
            "labels": {"strimzi.io/cluster": cluster},
        },
        "spec": {
            "replicas": replicas if replicas is not None else 1,
            "roles": ["broker"],
            "storage": {"type": "jbod", "volumes": [{"id": 0, "type": "ephemeral"}]},
        },
    }

    from kfk.commons import create_temp_file

    node_pool_yaml = yaml.dump(node_pool_dict)
    temp_file = create_temp_file(node_pool_yaml)
    create_using_yaml(temp_file.name, namespace)
    temp_file.close()


def delete(node_pool, cluster, namespace):
    if node_pool in DEFAULT_NODE_POOLS:
        defaults = ", ".join(DEFAULT_NODE_POOLS)
        click.echo(
            f"Cannot delete default node pool '{node_pool}'. "
            f"Default node pools ({defaults}) are required."
        )
        return

    node_pool_dict = {
        "apiVersion": "kafka.strimzi.io/v1beta2",
        "kind": "KafkaNodePool",
        "metadata": {
            "name": node_pool,
            "namespace": namespace,
            "labels": {"strimzi.io/cluster": cluster},
        },
    }

    from kfk.commons import create_temp_file

    node_pool_yaml = yaml.dump(node_pool_dict)
    temp_file = create_temp_file(node_pool_yaml)
    delete_using_yaml(temp_file.name, namespace)
    temp_file.close()
