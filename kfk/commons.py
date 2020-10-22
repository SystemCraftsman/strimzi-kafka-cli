import os
import io
import tempfile
import ntpath
import click

from kfk.kubectl_command_builder import Kubectl
from kfk.utils import convert_string_to_type
from kfk.constants import *
from subprocess import call


def print_missing_options_for_command(command_str):
    click.echo("Missing options: kfk {command_str} [OPTIONS] \nTry 'kfk {command_str} --help' for help.".format(
        command_str=command_str))


def print_resource_not_found_msg(cluster, namespace):
    click.echo("No resource found in Kafka cluster: {cluster}, namespace: {namespace}".format(
        cluster=cluster, namespace=namespace))


def delete_last_applied_configuration(resource_dict):
    if "annotations" in resource_dict["metadata"]:
        del resource_dict["metadata"]["annotations"]["kubectl.kubernetes.io/last-applied-configuration"]


def add_resource_kv_config(config, dict_part, *converters):
    if type(config) is tuple:
        for config_str in config:
            for converter in converters:
                config_str = converter(config_str)
            config_arr = get_kv_config_arr(config_str)
            dict_part[config_arr[0]] = convert_string_to_type(config_arr[1])
    else:
        config_arr = get_kv_config_arr(config)
        dict_part[config_arr[0]] = convert_string_to_type(config_arr[1])


def get_kv_config_arr(config_str):
    # TODO: exception here
    return config_str.split('=')


def delete_resource_config(config, dict_part, *converters):
    if type(config) is tuple:
        for config_str in config:
            for converter in converters:
                config_str = converter(config_str)
            if config_str in dict_part:
                del dict_part[config_str]
    else:
        del dict_part[config]


def resource_exists(resource_type, resource_name, cluster, namespace):
    return resource_name in os.popen(
        Kubectl().get().resource(resource_type).label("strimzi.io/cluster={cluster}").namespace(
            namespace).build().format(
            cluster=cluster)).read()


def get_resource_yaml(resource_type, resource_name, namespace):
    return os.popen(
        Kubectl().get().resource(resource_type, resource_name).namespace(namespace).output("yaml").build()).read()


def get_resource_as_stream(resource_type, resource_name, namespace):
    topic_yaml = get_resource_yaml(resource_type, resource_name, namespace)
    return io.StringIO(topic_yaml)


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
                    producer_property_arr = get_kv_config_arr(producer_property)
                    if producer_property_arr[1] == KAFKA_SSL:
                        port = KAFKA_SECURE_PORT
                if "ssl.truststore.location" in producer_property or "ssl.keystore.location" in producer_property:
                    producer_property_arr = get_kv_config_arr(producer_property)
                    file_path = producer_property_arr[1]
                    new_file_path = "/tmp/" + ntpath.basename(file_path)
                    transfer_file_to_container(file_path, new_file_path, container, pod, namespace)
                    producer_property = producer_property_arr[0] + "=" + new_file_path
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


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'
