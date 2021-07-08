import click
import os
import yaml

from kfk.commands.connect import connect
from kfk.commons import *
from kfk.config import *
from kfk.messages import Errors
from kfk.constants import *
from kfk.messages import Messages
from kfk.utils import is_valid_url
from kfk import argument_extensions, option_extensions
from kfk.commands.connect import connectors

CONNECT_SKIPPED_PROPERTIES = (
    SpecialTexts.CONNECT_BOOTSTRAP_SERVERS, SpecialTexts.CONNECT_IMAGE, SpecialTexts.CONNECT_PLUGIN_URL,
    SpecialTexts.CONNECT_PLUGIN_PATH)


@click.option('-y', '--yes', 'is_yes', help='"Yes" confirmation', is_flag=True)
@click.option('-n', '--namespace', help='Namespace to use')
@click.option('--alter', 'is_alter', help='Alters the connect cluster.', is_flag=True)
@click.option('--delete', 'is_delete', help='Deletes the connect cluster.', is_flag=True)
@click.argument('connector_config_files', nargs=-1, type=click.File('r'))
@click.argument('config_file', type=click.File('r'), cls=argument_extensions.RequiredIf, arguments=['is_create'])
@click.option('-p', '--registry-password', help='Image registry password for Connect image')
@click.option('-u', '--registry-username', help='Image registry username for Connect image')
@click.option('--replicas', help='The number of connect replicas for the cluster.', type=int)
@click.option('--create', 'is_create', help='Creates a new connect cluster.', is_flag=True)
@click.option('--describe', 'is_describe', help='List details for the given cluster.', is_flag=True)
@click.option('-o', '--output',
              help='Output format. One of: json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath'
                   '|jsonpath-file.')
@click.option('--list', 'is_list', help='Lists all available clusters.', required=True, is_flag=True)
@click.option('--cluster', help='Connect cluster name', required=True, cls=option_extensions.NotRequiredIf,
              options=['is_list'])
@connect.command()
def clusters(cluster, is_list, is_create, replicas, registry_username, registry_password, config_file,
             connector_config_files, is_describe, is_delete, is_alter, output, namespace, is_yes):
    """Creates, alters, deletes, describes Kafka Connect cluster(s)"""
    if is_list:
        list(namespace)
    elif is_create:
        create(cluster, replicas, registry_username, registry_password, config_file, connector_config_files, namespace,
               is_yes)
    elif is_describe:
        describe(cluster, output, namespace)
    elif is_delete:
        delete(cluster, namespace, is_yes)
    elif is_alter:
        alter(cluster, replicas, config_file, namespace)
    else:
        print_missing_options_for_command("connect")


def list(namespace):
    os.system(Kubectl().get().kafkaconnects().namespace(namespace).build())


def create(cluster, replicas, registry_username, registry_password, config_file, connector_config_files, namespace,
           is_yes):
    with open('{strimzi_path}/examples/connect/kafka-connect.yaml'.format(strimzi_path=STRIMZI_PATH).format(
            version=STRIMZI_VERSION)) as file:
        cluster_dict = yaml.full_load(file)

        cluster_dict["metadata"]["name"] = cluster

        cluster_dict["metadata"]["annotations"] = {}
        cluster_dict["metadata"]["annotations"]["strimzi.io/use-connector-resources"] = TRUE

        if replicas is not None:
            cluster_dict["spec"]["replicas"] = replicas

        connect_properties = get_properties_from_file(config_file)

        cluster_dict["spec"].pop("tls")

        cluster_dict["spec"]["bootstrapServers"] = connect_properties.get(
            SpecialTexts.CONNECT_BOOTSTRAP_SERVERS).data

        if connect_properties.get(SpecialTexts.CONNECT_PLUGIN_URL) is None:
            cluster_dict["spec"]["image"] = connect_properties.get(
                SpecialTexts.CONNECT_IMAGE).data
        else:
            cluster_dict["spec"]["build"] = {}
            cluster_dict["spec"]["build"]["output"] = {}
            cluster_dict["spec"]["build"]["output"]["type"] = CONNECT_OUTPUT_TYPE_DOCKER
            cluster_dict["spec"]["build"]["output"]["image"] = connect_properties.get(SpecialTexts.CONNECT_IMAGE).data
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

        add_properties_config_to_resource(connect_properties, cluster_dict["spec"]["config"],
                                          _return_if_not_skipped)

        cluster_yaml = yaml.dump(cluster_dict)
        cluster_temp_file = create_temp_file(cluster_yaml)

        if is_yes:
            is_confirmed = True
        else:
            open_file_in_system_editor(cluster_temp_file.name)
            is_confirmed = click.confirm(Messages.CLUSTER_CREATE_CONFIRMATION)

        if is_confirmed:
            return_code = 0

            if connect_properties.get(SpecialTexts.CONNECT_PLUGIN_URL) is not None:
                username = registry_username if registry_username is not None else click.prompt(
                    Messages.IMAGE_REGISTRY_USER_NAME, hide_input=False)
                password = registry_password if registry_password is not None else click.prompt(
                    Messages.IMAGE_REGISTRY_PASSWORD, hide_input=True)

                return_code = os.system(
                    Kubectl().create().secret("docker-registry", f"{cluster}-push-secret",
                                              "--docker-username={username}", "--docker-password={password}",
                                              "--docker-server={server}").namespace(
                        namespace).build().format(username=username, password=password, server=connect_properties.get(
                        SpecialTexts.CONNECT_IMAGE).data))

            if return_code == 0:
                return_code = os.system(
                    Kubectl().create().from_file("{cluster_temp_file_path}").namespace(namespace).build().format(
                        cluster_temp_file_path=cluster_temp_file.name))
                if return_code == 0:
                    for connector_config_file in connector_config_files:
                        connectors.create(connector_config_file, cluster, namespace)

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


def alter(cluster, replicas, config_file, namespace):
    if config_file is not None or replicas is not None:
        stream = get_resource_as_stream("kafkaconnects", resource_name=cluster, namespace=namespace)
        cluster_dict = yaml.full_load(stream)

        delete_last_applied_configuration(cluster_dict)

        if replicas is not None:
            cluster_dict["spec"]["replicas"] = replicas

        if config_file is not None:
            connect_properties = get_properties_from_file(config_file)

            cluster_dict["spec"]["bootstrapServers"] = connect_properties.get(
                SpecialTexts.CONNECT_BOOTSTRAP_SERVERS).data

            if connect_properties.get(SpecialTexts.CONNECT_PLUGIN_URL) is None:
                cluster_dict["spec"].pop("build", None)
                cluster_dict["spec"]["image"] = connect_properties.get(SpecialTexts.CONNECT_IMAGE).data
            else:
                cluster_dict["spec"].pop("image", None)
                cluster_dict["spec"]["build"]["output"]["image"] = connect_properties.get(
                    SpecialTexts.CONNECT_IMAGE).data

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

            add_properties_config_to_resource(connect_properties, cluster_dict["spec"]["config"],
                                              _return_if_not_skipped)

        cluster_yaml = yaml.dump(cluster_dict)
        cluster_temp_file = create_temp_file(cluster_yaml)
        os.system(
            Kubectl().replace().from_file("{cluster_temp_file_path}").namespace(namespace).build().format(
                cluster_temp_file_path=cluster_temp_file.name))
        cluster_temp_file.close()
    else:
        os.system(Kubectl().edit().kafkaconnects(cluster).namespace(namespace).build())


def _return_if_not_skipped(property_item):
    if property_item[0] not in CONNECT_SKIPPED_PROPERTIES:
        return property_item
    else:
        return None


def _get_plugin_type(plugin_url):
    if plugin_url.find(EXTENSION_TAR_GZ) > -1:
        return "tgz"
    elif plugin_url.find(EXTENSION_JAR) > -1:
        return "jar"
    elif plugin_url.find(EXTENSION_ZIP) > -1:
        return "zip"
    else:
        raise click.ClickException(Errors.NO_PLUGIN_TYPE_DETECTED)
