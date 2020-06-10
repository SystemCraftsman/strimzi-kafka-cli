import os
import wget
import tarfile
import ssl
import io

from .constants import *
from .kubectl_command_builder import Kubectl
from .utils import convert_string_to_type

ssl._create_default_https_context = ssl._create_unverified_context


def download_strimzi_if_not_exists():
    if not os.path.exists(STRIMZI_PATH.format(version=STRIMZI_VERSION)):
        strimzi_tarfile_path = STRIMZI_PATH.format(version=STRIMZI_VERSION) + ".tar.gz"

        print("Strimzi files are not available. Downloading Strimzi {version}...".format(version=STRIMZI_VERSION))
        wget.download(STRIMZI_RELEASE_URL.format(version=STRIMZI_VERSION), strimzi_tarfile_path)
        print("\nExtracting Strimzi {version}...".format(version=STRIMZI_VERSION))
        tar = tarfile.open(strimzi_tarfile_path)
        tar.extractall(path=BASE_PATH)
        tar.close()
        print("Deleting {file} file".format(file=strimzi_tarfile_path))
        os.remove(strimzi_tarfile_path)


def print_missing_options_for_command(command_str):
    print("Missing options: kfk {command_str} [OPTIONS] \nTry 'kfk {command_str} --help' for help.".format(
        command_str=command_str))


def delete_last_applied_configuration(resource_dict):
    if "annotations" in resource_dict["metadata"]:
        del resource_dict["metadata"]["annotations"]["kubectl.kubernetes.io/last-applied-configuration"]


def add_resource_kv_config(config, dict_part):
    if type(config) is tuple:
        for config_str in config:
            config_arr = config_str.split('=')
            dict_part[config_arr[0]] = convert_string_to_type(config_arr[1])
    else:
        config_arr = config.split('=')
        dict_part[config_arr[0]] = convert_string_to_type(config_arr[1])


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