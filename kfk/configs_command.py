import click
import os
import yaml

from kfk.command import kfk
from kfk import topics_command
from kfk.commons import print_missing_options_for_command


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--describe', help='List configs for the given entity.')
@click.option('--delete-config', help='Config keys to remove', multiple=True)
@click.option('--add-config', help='Key Value pairs of configs to add.', multiple=True)
@click.option('--entity-name', help='Name of entity', required=True)
@click.option('--entity-type', help='Type of entity (topics/users/clusters)', required=True)
@kfk.command()
def configs(entity_type, entity_name, add_config, delete_config, describe, cluster, namespace):
    """Add/Remove entity config for a topic, client, user or broker"""
    if len(add_config) > 0 or len(delete_config) > 0 or (describe is not None):
        if entity_type == "topics":
            topics_command.alter(entity_name, None, None, add_config, delete_config, cluster, namespace)
    else:
        print_missing_options_for_command("configs")
