import click
import os
import yaml

from kfk.command import kfk
from kfk.commons import *
from kfk.option_extensions import NotRequiredIf, RequiredIf


# TODO enter command explanations
@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.argument('config_files', nargs=-1, type=click.File('r'))
@click.option('--replica-count', help='', type=int)
@click.option('--cluster', help='Connect cluster name')
@click.option('--create', 'is_create', help='Create a new connect cluster.', is_flag=True)
@kfk.command()
def connect(is_create, cluster, replica_count, config_files, namespace):
    """Creates, alters, deletes, describes Kafka connect cluster(s) or connectors."""
    if is_create:
        if cluster is not None:
            if len(config_files) == 0:
                raise click.ClickException("A configuration file should be provided for connect cluster")

    else:
        print_missing_options_for_command("connect")
