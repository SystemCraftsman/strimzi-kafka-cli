import json

import click
import yaml

from kfk.commands.main import kfk
from kfk.kubernetes_commons import describe_resource, get_resource, list_resource
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
    "--describe",
    "is_describe",
    help="Describe a KafkaMirrorMaker2.",
    is_flag=True,
)
@click.option("--list", "is_list", help="List KafkaMirrorMaker2s.", is_flag=True)
@click.option(
    "--mm2",
    help="KafkaMirrorMaker2 name",
    required=True,
    cls=NotRequiredIf,
    options=["is_list"],
)
@kfk.command(name="mm2s")
def mirror_maker_2(mm2, is_list, is_describe, output, namespace):
    """Lists, describes KafkaMirrorMaker2(s)."""
    if is_list:
        list(namespace)
    elif is_describe:
        describe(mm2, output, namespace)


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
