import click
import os
import yaml

from kfk.commands.main import kfk
from kfk.kubectl_command_builder import Kubectl
from kfk.commands import topics
from kfk.commands import users
from kfk.commands import clusters
from kfk.commons import *
from kfk.constants import *
from kfk.messages import Messages
from kfk.option_extensions import NotRequiredIf


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--delete-config', help='Config keys to remove')
@click.option('--add-config', help='Key Value pairs of configs to add.')
@click.option('--alter', help='Alter the configuration for the entity.', is_flag=True)
@click.option('--native', help='List configs for the given entity natively.', is_flag=True)
@click.option('--describe', help='List configs for the given entity.', is_flag=True)
@click.option('--entity-name', help='Name of entity', required=True, cls=NotRequiredIf, options=['native'])
@click.option('--entity-type', help='Type of entity (topics/users/brokers)',
              type=click.Choice(['topics', 'users', 'brokers'], case_sensitive=True))
@kfk.command()
def configs(entity_type, entity_name, describe, native, alter, add_config, delete_config, cluster, namespace):
    """Adds/Removes entity config for a topic, client, user or brokers"""
    if describe:
        if entity_type == "topics":
            if native:
                _describe_natively(entity_type, entity_name, cluster, namespace)
            else:
                topics.describe(entity_name, None, False, None, cluster, namespace)
        elif entity_type == "users":
            if native:
                _describe_natively(entity_type, entity_name, cluster, namespace)
            else:
                users.describe(entity_name, None, cluster, namespace)
        elif entity_type == "brokers":
            if native:
                _describe_natively(entity_type, entity_name, cluster, namespace)
                stream = get_resource_as_stream("configmap", resource_name=cluster + "-kafka-config",
                                                namespace=namespace)
                config_dict = yaml.full_load(stream)
                config_data = get_list_by_split_string(config_dict["data"]["server.config"],
                                                       SpecialTexts.BROKER_CONFIG_FILE_USER_CONFIG_HEADER)[1]
                click.echo(NEW_LINE + Messages.USER_PROVIDED_CONFIG_HEADER + NEW_LINE + config_data)
            else:
                clusters.describe(cluster, None, namespace)

    elif alter:
        add_config_list = get_config_list(add_config)
        delete_config_list = get_config_list(delete_config)

        if entity_type == "topics":
            topics.alter(entity_name, None, None, add_config_list, delete_config_list, cluster, namespace)
        elif entity_type == "users":
            users.alter(entity_name, None, None, False, False, tuple(), None, None, None, None, None,
                        add_config_list, delete_config_list, cluster, namespace)
        elif entity_type == "brokers":
            clusters.alter(entity_name, None, None, add_config_list, delete_config_list, namespace)
    else:
        print_missing_options_for_command("configs")


def _describe_natively(entity_type, entity_name, cluster, namespace):
    native_command = "bin/kafka-configs.sh --bootstrap-server {cluster}-kafka-brokers:{port} " \
                     "--entity-type {entity_type} --describe"

    if entity_name is not None:
        native_command = native_command + SPACE + "--entity-name {entity_name}"

        if entity_type == "users":
            entity_name = COMMON_NAME_PREFIX + entity_name

    os.system(
        Kubectl().exec("-it", cluster + "-kafka-0").container("kafka").namespace(namespace).exec_command(
            native_command).build().format(cluster=cluster, port=KAFKA_PORT, entity_type=entity_type,
                                           entity_name=entity_name))
