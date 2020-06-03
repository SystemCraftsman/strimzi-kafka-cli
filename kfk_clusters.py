import click
import os

from kfk import kfk
from option_extensions import NotRequiredIf
from commons import print_missing_options_for_command


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('--describe', help='List details for the given cluster.', is_flag=True)
@click.option('--list', help='List all available clusters.', required=True, is_flag=True)
@click.option('--cluster', help='Cluster Name', required=True, cls=NotRequiredIf, not_required_if='list')
@kfk.command()
def clusters(cluster, list, describe, namespace):
    """The kafka cluster(s) to be created, altered or described. """
    if list:
        os.system('kubectl get kafkas -n {namespace}'.format(namespace=namespace))
    elif describe:
        os.system(
            'kubectl describe kafkas {cluster} -n {namespace}'.format(cluster=cluster, namespace=namespace))
    else:
        print_missing_options_for_command("clusters")