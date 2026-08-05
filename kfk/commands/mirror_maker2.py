import json

import click
import yaml

from kfk.commands.main import kfk
from kfk.commons import create_temp_file
from kfk.kubernetes_commons import (
    create_using_yaml,
    delete_using_yaml,
    describe_resource,
    get_resource,
    list_resource,
)
from kfk.option_extensions import NotRequiredIf


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
    "--source",
    help="Source cluster bootstrap servers.",
)
@click.option(
    "--target",
    help="Target cluster bootstrap servers.",
)
@click.option(
    "--mm2",
    help="KafkaMirrorMaker2 name",
    required=True,
    cls=NotRequiredIf,
    options=["is_list"],
)
@kfk.command(name="mm2s")
def mirror_maker_2(
    mm2,
    target,
    source,
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
        describe(mm2, output, namespace)
    elif is_create:
        create(mm2, source, target, namespace)
    elif is_delete:
        delete(mm2, namespace)


def list(namespace):
    return list_resource("kafkamirrormaker2s", namespace)


def describe(mm2, output, namespace):
    if output is not None:
        resource = get_resource("kafkamirrormaker2s", mm2, namespace)
        if output == "yaml":
            click.echo(yaml.dump(resource, default_flow_style=False))
        elif output == "json":
            click.echo(json.dumps(resource, indent=2))
    else:
        describe_resource("kafkamirrormaker2s", mm2, namespace)


def create(mm2, source, target, namespace):
    mm2_dict = {
        "apiVersion": "kafka.strimzi.io/v1beta2",
        "kind": "KafkaMirrorMaker2",
        "metadata": {"name": mm2},
        "spec": {
            "version": "4.2.0",
            "replicas": 1,
            "connectCluster": "target",
            "clusters": [
                {
                    "alias": "source",
                    "bootstrapServers": source,
                },
                {
                    "alias": "target",
                    "bootstrapServers": target,
                },
            ],
            "mirrors": [
                {
                    "sourceCluster": "source",
                    "targetCluster": "target",
                    "sourceConnector": {"tasksMax": 2},
                    "topicsPattern": ".*",
                    "groupsPattern": ".*",
                }
            ],
        },
    }

    mm2_yaml = yaml.dump(mm2_dict)
    temp_file = create_temp_file(mm2_yaml)
    create_using_yaml(temp_file.name, namespace)
    temp_file.close()


def delete(mm2, namespace):
    mm2_dict = {
        "apiVersion": "kafka.strimzi.io/v1beta2",
        "kind": "KafkaMirrorMaker2",
        "metadata": {"name": mm2, "namespace": namespace},
    }

    mm2_yaml = yaml.dump(mm2_dict)
    temp_file = create_temp_file(mm2_yaml)
    delete_using_yaml(temp_file.name, namespace)
    temp_file.close()
