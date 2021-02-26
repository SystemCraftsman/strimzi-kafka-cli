import click
import os
import yaml

from kfk.command import kfk
from kfk.commons import *


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('--cluster', help='Connect cluster name')
@click.option('--create', 'is_create', help='Create a new connect cluster.', is_flag=True)
@kfk.command()
def connect(is_create, cluster, namespace):
    """Creates, alters, deletes, describes Kafka connect cluster(s) or connectors."""
    print_missing_options_for_command("connect")
