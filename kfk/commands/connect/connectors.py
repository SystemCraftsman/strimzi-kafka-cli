import click
import os
import yaml

from kfk.commands.connect import connect
from kfk.commons import print_missing_options_for_command
from kfk import argument_extensions, option_extensions
from kfk.kubectl_command_builder import Kubectl
from kfk.config import *
from kfk.commons import *

CONNECTOR_SKIPPED_PROPERTIES = (
    SpecialTexts.CONNECTOR_NAME, SpecialTexts.CONNECTOR_TASKS_MAX, SpecialTexts.CONNECTOR_CLASS)


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Connect cluster to use', required=True)
@click.option('--alter', 'is_alter', help='Alter the connector.', is_flag=True)
@click.option('--delete', 'is_delete', help='Delete the connector.', is_flag=True)
@click.option('-o', '--output',
              help='Output format. One of: json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath'
                   '|jsonpath-file.')
@click.option('--describe', 'is_describe', help='List details for the given connector.', is_flag=True)
@click.argument('config_file', type=click.File('r'), cls=argument_extensions.NotRequiredIf,
                arguments=['is_describe', 'is_delete', 'is_list'])
@click.option('--create', 'is_create', help='Create a new connector.', is_flag=True)
@click.option('--list', 'is_list', help='List all available connectors.', is_flag=True)
@click.option('--connector', help='Connector Name', cls=option_extensions.RequiredIf,
              options=['is_describe', 'is_delete'])
@connect.command()
def connectors(connector, is_list, is_create, config_file, is_describe, output, is_delete, is_alter, cluster,
               namespace):
    """Creates, alters, deletes, describes Kafka Connect connector(s)."""
    if is_list:
        list(cluster, namespace)
    elif is_create:
        create(config_file, cluster, namespace)
    elif is_describe:
        describe(connector, output, namespace)
    elif is_delete:
        delete(connector, namespace)
    elif is_alter:
        alter(config_file, cluster, namespace)
    else:
        print_missing_options_for_command("connectors")


def list(cluster, namespace):
    os.system(
        Kubectl().get().kafkaconnectors().label("strimzi.io/cluster={cluster}").namespace(namespace).build().format(
            cluster=cluster))


def create(config_file, cluster, namespace):
    with open('{strimzi_path}/examples/connect/source-connector.yaml'.format(strimzi_path=STRIMZI_PATH).format(
            version=STRIMZI_VERSION)) as file:
        connector_dict = yaml.full_load(file)

        connector_properties = get_properties_from_file(config_file)

        connector_dict["metadata"]["name"] = connector_properties.get(SpecialTexts.CONNECTOR_NAME).data
        connector_dict["metadata"]["labels"]["strimzi.io/cluster"] = cluster

        connector_dict["spec"]["class"] = connector_properties.get(SpecialTexts.CONNECTOR_CLASS).data
        connector_dict["spec"]["tasksMax"] = int(connector_properties.get(SpecialTexts.CONNECTOR_TASKS_MAX).data)
        connector_dict["spec"]["config"] = {}

        add_properties_config_to_resource(connector_properties, connector_dict["spec"]["config"],
                                          _return_if_not_skipped)

        connector_yaml = yaml.dump(connector_dict)
        connector_temp_file = create_temp_file(connector_yaml)

        os.system(
            Kubectl().create().from_file("{connector_temp_file_path}").namespace(namespace).build().format(
                connector_temp_file_path=connector_temp_file.name))

        connector_temp_file.close()


def describe(connector, output, namespace):
    if output is not None:
        os.system(Kubectl().get().kafkaconnectors(connector).namespace(namespace).output(output).build())
    else:
        os.system(Kubectl().describe().kafkaconnectors(connector).namespace(namespace).build())


def delete(connector, namespace):
    os.system(Kubectl().delete().kafkaconnectors(connector).namespace(namespace).build())


def alter(config_file, cluster, namespace):
    connector_properties = get_properties_from_file(config_file)

    stream = get_resource_as_stream("kafkaconnectors",
                                    resource_name=connector_properties.get(SpecialTexts.CONNECTOR_NAME).data,
                                    namespace=namespace)

    connector_dict = yaml.full_load(stream)

    delete_last_applied_configuration(connector_dict)

    connector_dict["spec"]["class"] = connector_properties.get(SpecialTexts.CONNECTOR_CLASS).data
    connector_dict["spec"]["tasksMax"] = int(connector_properties.get(SpecialTexts.CONNECTOR_TASKS_MAX).data)

    connector_dict["spec"]["config"] = {}

    add_properties_config_to_resource(connector_properties, connector_dict["spec"]["config"],
                                      _return_if_not_skipped)

    connector_yaml = yaml.dump(connector_dict)
    connector_temp_file = create_temp_file(connector_yaml)

    os.system(
        Kubectl().replace().from_file("{topic_temp_file_path}").namespace(namespace).build().format(
            topic_temp_file_path=connector_temp_file.name))

    connector_temp_file.close()


def _return_if_not_skipped(property_item):
    if property_item[0] not in CONNECTOR_SKIPPED_PROPERTIES:
        return property_item
    else:
        return None
