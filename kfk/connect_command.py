import click
import os
import yaml

from kfk.command import kfk
from kfk.commons import *


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('--cluster', help='Connect cluster name')
@kfk.command()
def connect(cluster, namespace):
    """Creates, alters, deletes, describes Kafka connect cluster(s) or connectors."""
    print_missing_options_for_command("connect")
