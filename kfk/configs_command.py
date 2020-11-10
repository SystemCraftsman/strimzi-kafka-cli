import click
import os

from kfk.command import kfk
from kfk.kubectl_command_builder import Kubectl
from kfk import topics_command
from kfk import users_command
from kfk import clusters_command
from kfk.commons import print_missing_options_for_command
from kfk.constants import *


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--delete-config', help='Config keys to remove', multiple=True)
@click.option('--add-config', help='Key Value pairs of configs to add.', multiple=True)
@click.option('--alter', help='Alter the configuration for the entity.', is_flag=True)
@click.option('--native', help='List configs for the given entity natively.', is_flag=True)
@click.option('--describe', help='List configs for the given entity.', is_flag=True)
@click.option('--entity-name', help='Name of entity', required=True)
@click.option('--entity-type', help='Type of entity (topics/users/brokers)',
              type=click.Choice(['topics', 'users', 'brokers'], case_sensitive=True))
@kfk.command()
def configs(entity_type, entity_name, describe, native, alter, add_config, delete_config, cluster, namespace):
    """Add/Remove entity config for a topic, client, user or cluster"""
    if describe:
        if entity_type == "topics":
            if native:
                native_command = "bin/kafka-configs.sh --bootstrap-server {cluster}-kafka-brokers:{port} --entity-type " \
                                 "{entity_type} --entity-name {entity_name} --describe"
                os.system(
                    Kubectl().exec("-it", cluster + "-kafka-0").container("kafka").namespace(namespace).exec_command(
                        native_command).build().format(cluster=cluster, port=KAFKA_PORT, entity_type=entity_type,
                                                       entity_name=entity_name))
            else:
                topics_command.describe(entity_name, None, False, None, cluster, namespace)
        elif entity_type == "users":
            click.echo("Not implemented")
        elif entity_type == "brokers":
            click.echo("Not implemented")

    elif alter:
        if len(add_config) > 0 or len(delete_config) > 0:
            if entity_type == "topics":
                topics_command.alter(entity_name, None, None, add_config, delete_config, cluster, namespace)
            elif entity_type == "users":
                users_command.alter(entity_name, None, None, False, False, tuple(), None, None, None, None, None,
                                    add_config, delete_config, cluster, namespace)
            elif entity_type == "brokers":
                if entity_name == "all":
                    clusters_command.alter(cluster, add_config, delete_config, namespace)
                else:
                    click.echo("`entity-name` for brokers should be set as `all`", err=True)
    else:
        print_missing_options_for_command("configs")
