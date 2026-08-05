import json

import click
import yaml

from kfk.commands.main import kfk
from kfk.kubernetes_commons import describe_resource, get_resource, list_resource
from kfk.option_extensions import NotRequiredIf


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
    "--describe",
    "is_describe",
    help="Describe a KafkaNodePool.",
    is_flag=True,
)
@click.option("--list", "is_list", help="List KafkaNodePools.", is_flag=True)
@click.option(
    "--node-pool",
    help="KafkaNodePool name",
    required=True,
    cls=NotRequiredIf,
    options=["is_list"],
)
@kfk.command(name="node-pools")
def node_pools(node_pool, is_list, is_describe, output, cluster, namespace):
    """Lists, describes KafkaNodePool(s)."""
    if is_list:
        list(cluster, namespace)
    elif is_describe:
        describe(node_pool, output, cluster, namespace)


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
