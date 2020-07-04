import os
import io
import tempfile

from kfk.kubectl_command_builder import Kubectl
from kfk.utils import convert_string_to_type


def print_missing_options_for_command(command_str):
    print("Missing options: kfk {command_str} [OPTIONS] \nTry 'kfk {command_str} --help' for help.".format(
        command_str=command_str))


def print_resource_found_msg(cluster, namespace):
    print("No resource found in Kafka cluster: {cluster}, namespace: {namespace}".format(
        cluster=cluster, namespace=namespace))


def delete_last_applied_configuration(resource_dict):
    if "annotations" in resource_dict["metadata"]:
        del resource_dict["metadata"]["annotations"]["kubectl.kubernetes.io/last-applied-configuration"]


def add_resource_kv_config(config, dict_part):
    if type(config) is tuple:
        for config_str in config:
            config_arr = get_kv_config_arr(config_str)
            dict_part[config_arr[0]] = convert_string_to_type(config_arr[1])
    else:
        config_arr = get_kv_config_arr(config)
        dict_part[config_arr[0]] = convert_string_to_type(config_arr[1])


def get_kv_config_arr(config_str):
    # TODO: exception here
    return config_str.split('=')


def delete_resource_config(config, dict_part):
    if type(config) is tuple:
        for config_str in config:
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


def get_resource_as_file(resource_type, resource_name, namespace):
    topic_yaml = get_resource_yaml(resource_type, resource_name, namespace)
    return io.StringIO(topic_yaml)


def create_temp_file(content):
    temp_file = tempfile.NamedTemporaryFile(mode='w+')
    temp_file.write(content)
    temp_file.flush()
    return temp_file


def transfer_file_to_container(source_file_path, dest_file_path, container, pod, namespace):
    os.system(Kubectl().cp(source_file_path, "{namespace}/{pod}:" + dest_file_path).container(container).build().format(
        namespace=namespace, pod=pod))


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'
