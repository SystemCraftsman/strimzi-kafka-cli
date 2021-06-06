import click
import os
import yaml

from kfk.commands.main import kfk
from kfk.commons import *
from kfk.config import *
from kfk.messages import Errors
from kfk.constants import *
from jproperties import Properties
from kfk.messages import Messages
from kfk.utils import is_valid_url
from kfk.option_extensions import NotRequiredIf

CONNECT_SKIPPED_PROPERTIES = (
    SpecialTexts.CONNECT_BOOTSTRAP_SERVERS, SpecialTexts.CONNECT_OUTPUT_IMAGE, SpecialTexts.CONNECT_PLUGIN_URL,
    SpecialTexts.CONNECT_PLUGIN_PATH)


@click.option('-y', '--yes', 'is_yes', help='"Yes" confirmation', is_flag=True)
@click.option('-n', '--namespace', help='Namespace to use')
@click.option('--alter', 'is_alter', help='Alter the cluster.', is_flag=True)
@click.option('--delete', 'is_delete', help='Delete the cluster.', is_flag=True)
@click.argument('config_files', nargs=-1, type=click.File('r'))
@click.option('-p', '--registry-password', help='Image registry password for Connect image')
@click.option('-u', '--registry-username', help='Image registry username for Connect image')
@click.option('--replicas', help='The number of connect replicas for the cluster.', type=int)
@click.option('--create', 'is_create', help='Create a new connect cluster.', is_flag=True)
@click.option('--describe', 'is_describe', help='List details for the given cluster.', is_flag=True)
@click.option('-o', '--output',
              help='Output format. One of: json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath'
                   '|jsonpath-file.')
@click.option('--list', 'is_list', help='List all available clusters.', required=True, is_flag=True)
@click.option('--cluster', help='Connect cluster name', required=True, cls=NotRequiredIf, not_required_if=['is_list'])
@kfk.command()
def connect(cluster, is_list, is_create, replicas, registry_username, registry_password, config_files, is_describe,
            is_delete, is_alter, output, namespace, is_yes):
    """Creates, alters, deletes, describes Kafka Connect cluster(s) or its connectors."""
    if is_list:
        list(namespace)
    if is_create:
        create(cluster, replicas, registry_username, registry_password, config_files, namespace, is_yes)
    elif is_describe:
        describe(cluster, output, namespace)
    elif is_delete:
        delete(cluster, namespace, is_yes)
    elif is_alter:
        alter(cluster, replicas, config_files, namespace)
    else:
        print_missing_options_for_command("connect")


def list(namespace):
    os.system(Kubectl().get().kafkaconnects().namespace(namespace).build())


def create(cluster, replicas, registry_username, registry_password, config_files, namespace, is_yes):
    if cluster is not None:
        if len(config_files) == 0:
            raise click.ClickException(Errors.CONFIG_FILE_SHOULD_BE_PROVIDED)

        with open('{strimzi_path}/examples/connect/kafka-connect.yaml'.format(strimzi_path=STRIMZI_PATH).format(
                version=STRIMZI_VERSION)) as file:
            cluster_dict = yaml.full_load(file)

            cluster_dict["metadata"]["name"] = cluster

            if replicas is not None:
                cluster_dict["spec"]["replicas"] = replicas

            connect_properties = Properties()
            connect_properties.load(config_files[0].read())

            del cluster_dict["spec"]["tls"]

            cluster_dict["spec"]["bootstrapServers"] = connect_properties.get(
                SpecialTexts.CONNECT_BOOTSTRAP_SERVERS).data

            cluster_dict["spec"]["build"] = {}
            cluster_dict["spec"]["build"]["output"] = {}
            cluster_dict["spec"]["build"]["output"]["type"] = CONNECT_OUTPUT_TYPE_DOCKER
            cluster_dict["spec"]["build"]["output"]["image"] = connect_properties.get(
                SpecialTexts.CONNECT_OUTPUT_IMAGE).data
            cluster_dict["spec"]["build"]["output"]["pushSecret"] = f"{cluster}-push-secret"
            cluster_dict["spec"]["build"]["plugins"] = []

            for i, plugin_url in enumerate(
                    get_list_by_split_string(connect_properties.get(SpecialTexts.CONNECT_PLUGIN_URL).data, COMMA),
                    start=1):

                if not is_valid_url(plugin_url):
                    raise click.ClickException(Errors.NOT_A_VALID_URL + f": {plugin_url}")

                plugin_dict = {"name": f"connector-{i}",
                               "artifacts": [{"type": _get_plugin_type(plugin_url), "url": plugin_url}]}

                cluster_dict["spec"]["build"]["plugins"].append(plugin_dict)
            cluster_dict["spec"]["config"] = {}

            for item in connect_properties.items():
                if item[0] not in CONNECT_SKIPPED_PROPERTIES:
                    cluster_dict["spec"]["config"][item[0]] = item[1].data

            cluster_yaml = yaml.dump(cluster_dict)
            cluster_temp_file = create_temp_file(cluster_yaml)

            if is_yes:
                is_confirmed = True
            else:
                open_file_in_system_editor(cluster_temp_file.name)
                is_confirmed = click.confirm(Messages.CLUSTER_CREATE_CONFIRMATION)

            if is_confirmed:
                username = registry_username if registry_username is not None else click.prompt(
                    Messages.IMAGE_REGISTRY_USER_NAME, hide_input=False)
                password = registry_password if registry_password is not None else click.prompt(
                    Messages.IMAGE_REGISTRY_PASSWORD, hide_input=True)

                return_code = os.system(
                    Kubectl().create().secret("docker-registry", f"{cluster}-push-secret",
                                              "--docker-username={username}", "--docker-password={password}",
                                              "--docker-server={server}").namespace(
                        namespace).build().format(username=username, password=password, server=connect_properties.get(
                        SpecialTexts.CONNECT_OUTPUT_IMAGE).data))

                if return_code == 0:
                    os.system(
                        Kubectl().create().from_file("{cluster_temp_file_path}").namespace(namespace).build().format(
                            cluster_temp_file_path=cluster_temp_file.name))
            cluster_temp_file.close()


def describe(cluster, output, namespace):
    if output is not None:
        os.system(Kubectl().get().kafkaconnects(cluster).namespace(namespace).output(output).build())
    else:
        os.system(Kubectl().describe().kafkaconnects(cluster).namespace(namespace).build())


def delete(cluster, namespace, is_yes):
    if is_yes:
        is_confirmed = True
    else:
        is_confirmed = click.confirm(Messages.CLUSTER_DELETE_CONFIRMATION)
    if is_confirmed:
        return_code = os.system(Kubectl().delete().kafkaconnects(cluster).namespace(namespace).build())

        if return_code == 0:
            os.system(Kubectl().delete().secret(f"{cluster}-push-secret").namespace(
                namespace).build())


def alter(cluster, replicas, config_files, namespace):
    if len(config_files) > 0 or replicas is not None:
        stream = get_resource_as_stream("kafkaconnects", cluster, namespace)
        cluster_dict = yaml.full_load(stream)

        if replicas is not None:
            cluster_dict["spec"]["replicas"] = replicas

        connect_properties = Properties()
        if len(config_files) > 0:
            connect_properties.load(config_files[0].read())

            cluster_dict["spec"]["bootstrapServers"] = connect_properties.get(
                SpecialTexts.CONNECT_BOOTSTRAP_SERVERS).data

            cluster_dict["spec"]["build"]["output"]["image"] = connect_properties.get(
                SpecialTexts.CONNECT_OUTPUT_IMAGE).data

            cluster_dict["spec"]["build"]["plugins"] = []

            for i, plugin_url in enumerate(
                    get_list_by_split_string(connect_properties.get(SpecialTexts.CONNECT_PLUGIN_URL).data, COMMA),
                    start=1):

                if not is_valid_url(plugin_url):
                    raise click.ClickException(Errors.NOT_A_VALID_URL + f": {plugin_url}")

                plugin_dict = {"name": f"connector-{i}",
                               "artifacts": [{"type": _get_plugin_type(plugin_url), "url": plugin_url}]}

                cluster_dict["spec"]["build"]["plugins"].append(plugin_dict)
            cluster_dict["spec"]["config"] = {}

            for item in connect_properties.items():
                if item[0] not in CONNECT_SKIPPED_PROPERTIES:
                    cluster_dict["spec"]["config"][item[0]] = item[1].data

        cluster_yaml = yaml.dump(cluster_dict)
        cluster_temp_file = create_temp_file(cluster_yaml)
        os.system(
            Kubectl().apply().from_file("{cluster_temp_file_path}").namespace(namespace).build().format(
                cluster_temp_file_path=cluster_temp_file.name))
        cluster_temp_file.close()
    else:
        os.system(Kubectl().edit().kafkaconnects(cluster).namespace(namespace).build())


def _get_plugin_type(plugin_url):
    if plugin_url.find(EXTENSION_TAR_GZ) > -1:
        return "tgz"
    elif plugin_url.find(EXTENSION_JAR) > -1:
        return "jar"
    elif plugin_url.find(EXTENSION_ZIP) > -1:
        return "zip"
    else:
        raise click.ClickException(Errors.NO_PLUGIN_TYPE_DETECTED)


def _prepare_cluster_internals(cluster_dict, cluster, replicas, connect_properties):
    cluster_dict["metadata"]["name"] = cluster

    if replicas is not None:
        cluster_dict["spec"]["replicas"] = replicas

    del cluster_dict["spec"]["tls"]

    if len(connect_properties) > 0:
        cluster_dict["spec"]["bootstrapServers"] = connect_properties.get(SpecialTexts.CONNECT_BOOTSTRAP_SERVERS).data

        cluster_dict["spec"]["build"] = {}
        cluster_dict["spec"]["build"]["output"] = {}
        cluster_dict["spec"]["build"]["output"]["type"] = CONNECT_OUTPUT_TYPE_DOCKER
        cluster_dict["spec"]["build"]["output"]["image"] = connect_properties.get(
            SpecialTexts.CONNECT_OUTPUT_IMAGE).data
        cluster_dict["spec"]["build"]["output"]["pushSecret"] = f"{cluster}-push-secret"
        cluster_dict["spec"]["build"]["plugins"] = []

        for i, plugin_url in enumerate(
                get_list_by_split_string(connect_properties.get(SpecialTexts.CONNECT_PLUGIN_URL).data, COMMA), start=1):

            if not is_valid_url(plugin_url):
                raise click.ClickException(Errors.NOT_A_VALID_URL + f": {plugin_url}")

            plugin_dict = {"name": f"connector-{i}",
                           "artifacts": [{"type": _get_plugin_type(plugin_url), "url": plugin_url}]}

            cluster_dict["spec"]["build"]["plugins"].append(plugin_dict)
        cluster_dict["spec"]["config"] = {}

        for item in connect_properties.items():
            if item[0] not in CONNECT_SKIPPED_PROPERTIES:
                cluster_dict["spec"]["config"][item[0]] = item[1].data

    return cluster_dict
