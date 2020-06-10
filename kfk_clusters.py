import click
import os

from .kfk import kfk
from .option_extensions import NotRequiredIf
from .commons import print_missing_options_for_command
from .kubectl_command_builder import Kubectl


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-o', '--output',
              help='Output format. One of: json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath'
                   '|jsonpath-file.')
@click.option('--describe', help='List details for the given cluster.', is_flag=True)
@click.option('--list', help='List all available clusters.', required=True, is_flag=True)
@click.option('--cluster', help='Cluster Name', required=True, cls=NotRequiredIf, not_required_if='list')
@kfk.command()
def clusters(cluster, list, describe, output, namespace):
    """The kafka cluster(s) to be created, altered or described. """
    if list:
        os.system(Kubectl().get().kafkas().namespace(namespace).build())
    elif describe:
        if output is not None:
            os.system(
                Kubectl().get().kafkas(cluster).namespace(namespace).output(output).build())
        else:
            os.system(
                Kubectl().describe().kafkas(cluster).namespace(namespace).build())
    else:
        print_missing_options_for_command("clusters")
