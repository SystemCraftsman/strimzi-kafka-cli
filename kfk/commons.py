import os
import io
import tempfile
import ntpath
import click

from kfk.kubectl_command_builder import Kubectl
from kfk.utils import convert_string_to_type, get_list_by_split_string
from kfk.constants import *
from subprocess import call
from jproperties import Properties


# TODO: Message string to messages.py

def print_missing_options_for_command(command_str):
    click.echo("Missing options: kfk {command_str} [OPTIONS] \nTry 'kfk {command_str} --help' for help.".format(
        command_str=command_str))


def print_cluster_resource_not_found_msg(cluster, namespace):
    click.echo("No resource found in Kafka cluster: {cluster}, namespace: {namespace}".format(
        cluster=cluster, namespace=namespace))


def print_resource_not_found_msg(namespace):
    click.echo("No resource found in namespace: {namespace}".format(namespace=namespace))


def delete_last_applied_configuration(resource_dict):
    if "annotations" in resource_dict["metadata"]:
        resource_dict["metadata"]["annotations"].pop("kubectl.kubernetes.io/last-applied-configuration", None)


def add_kv_config_to_resource(config, dict_part, *converters):
    if type(config) is tuple or type(config) is list:
        for config_str in config:
            for converter in converters:
                config_str = converter(config_str)
            config_list = get_kv_config_list(config_str)
            dict_part[config_list[0]] = convert_string_to_type(config_list[1])
    else:
        for converter in converters:
            config = converter(config)
        config_list = get_kv_config_list(config)
        dict_part[config_list[0]] = convert_string_to_type(config_list[1])


def add_properties_config_to_resource(properties, dict_part, *converters):
    for property_item in properties.items():
        for converter in converters:
            property_item = converter(property_item)
            if property_item is not None:
                dict_part[property_item[0]] = convert_string_to_type(property_item[1].data)


def get_kv_config_list(config_str):
    return get_list_by_split_string(config_str, EQUALS)


def get_config_list(config_str):
    if config_str is None:
        return list()
    else:
        return get_list_by_split_string(config_str, COMMA)


def delete_resource_config(config, dict_part, *converters):
    if type(config) is tuple or type(config) is list:
        for config_str in config:
            for converter in converters:
                config_str = converter(config_str)
            dict_part.pop(config_str, None)
    else:
        dict_part.pop(config, None)


def resource_exists(resource_type=None, resource_name=None, cluster=None, namespace=None):
    command = Kubectl().get().resource(resource_type).namespace(namespace)

    if cluster is not None:
        command = command.label(f"strimzi.io/cluster={cluster}")

    return resource_name in os.popen(command.build()).read()


def get_resource_yaml(resource_type=None, resource_name=None, cluster=None, namespace=None):
    command = Kubectl().get().resource(resource_type, resource_name).namespace(namespace).output("yaml")

    if cluster is not None:
        command = command.label(f"strimzi.io/cluster={cluster}")

    return os.popen(command.build()).read()


def get_resource_as_stream(resource_type=None, resource_name=None, cluster=None, namespace=None):
    resource_yaml = get_resource_yaml(resource_type, resource_name, cluster, namespace)

    if not resource_yaml:
        raise click.exceptions.Exit(1)

    return io.StringIO(resource_yaml)


def create_temp_file(stream):
    temp_file = tempfile.NamedTemporaryFile(mode='w+')
    temp_file.write(stream)
    temp_file.flush()
    return temp_file


def open_file_in_system_editor(file):
    call([os.environ.get('EDITOR', 'vim'), file])


def transfer_file_to_container(source_file_path, dest_file_path, container, pod, namespace):
    os.system(Kubectl().cp(source_file_path, "{namespace}/{pod}:" + dest_file_path).container(container).build().format(
        namespace=namespace, pod=pod))


def apply_client_config_from_file(native_command, config_file_path, config_file_flag, container, pod, namespace):
    port = KAFKA_PORT
    delete_file_command = ""
    with open(config_file_path) as file:
        temp_file = create_temp_file(file.read())
        lines = []
        with open(temp_file.name) as temp_file:
            for cnt, producer_property in enumerate(temp_file):
                producer_property = producer_property.strip()
                if "security.protocol" in producer_property:
                    producer_property_list = get_kv_config_list(producer_property)
                    if producer_property_list[1] == KAFKA_SSL:
                        port = KAFKA_SECURE_PORT
                if "ssl.truststore.location" in producer_property or "ssl.keystore.location" in producer_property:
                    producer_property_list = get_kv_config_list(producer_property)
                    file_path = producer_property_list[1]
                    new_file_path = "/tmp/" + ntpath.basename(file_path)
                    transfer_file_to_container(file_path, new_file_path, container, pod, namespace)
                    producer_property = producer_property_list[0] + "=" + new_file_path
                    delete_file_command = delete_file_command + "rm -rf" + SPACE + new_file_path + SEMICOLON
                lines.append(producer_property)
        with open(temp_file.name, 'w') as temp_file:
            for line in lines:
                temp_file.write(line + NEW_LINE)
        new_config_file_path = "/tmp/" + ntpath.basename(config_file_path)
        transfer_file_to_container(temp_file.name, new_config_file_path, container, pod, namespace)
        delete_file_command = delete_file_command + "rm -rf" + SPACE + new_config_file_path + SEMICOLON
        native_command = native_command + SPACE + config_file_flag + SPACE + new_config_file_path
        temp_file.close()
    return native_command.format_map(SafeDict(port=port)) + SEMICOLON + delete_file_command


def get_properties_from_file(file):
    properties = Properties()
    properties.load(file.read())
    return properties


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'
