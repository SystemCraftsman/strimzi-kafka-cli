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

CONNECT_SKIPPED_PROPERTIES = (
    SpecialTexts.CONNECT_BOOTSTRAP_SERVERS, SpecialTexts.CONNECT_OUTPUT_IMAGE, SpecialTexts.CONNECT_OUTPUT_PUSH_SECRET,
    SpecialTexts.CONNECT_PLUGIN_URL, SpecialTexts.CONNECT_PLUGIN_PATH)


@click.option('-y', '--yes', 'is_yes', help='"Yes" confirmation', is_flag=True)
@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.argument('config_files', nargs=-1, type=click.File('r'))
@click.option('--replicas', help='The number of connect replicas for the cluster.', type=int)
@click.option('--cluster', help='Connect cluster name')
@click.option('--create', 'is_create', help='Create a new connect cluster.', is_flag=True)
@kfk.command()
def connect(is_create, cluster, replicas, config_files, namespace, is_yes):
    """Creates, alters, deletes, describes Kafka connect cluster(s) or connectors."""
    if is_create:
        create(cluster, replicas, config_files, namespace, is_yes)

    else:
        print_missing_options_for_command("connect")


def create(cluster, replicas, config_files, namespace, is_yes):
    if cluster is not None:
        if len(config_files) == 0:
            raise click.ClickException(Errors.CONFIG_FILE_SHOULD_BE_PROVIDED)

        with open('{strimzi_path}/examples/connect/kafka-connect.yaml'.format(strimzi_path=STRIMZI_PATH).format(
                version=STRIMZI_VERSION)) as file:
            cluster_dict = yaml.full_load(file)

            connect_properties = Properties()
            connect_properties.load(config_files[0].read())

            cluster_dict["metadata"]["name"] = cluster
            cluster_dict["spec"]["bootstrapServers"] = connect_properties.get(
                SpecialTexts.CONNECT_BOOTSTRAP_SERVERS).data
            cluster_dict["spec"]["tls"] = {}

            if replicas is not None:
                cluster_dict["spec"]["replicas"] = replicas

            cluster_dict["spec"]["build"] = {}
            cluster_dict["spec"]["build"]["output"] = {}

            cluster_dict["spec"]["build"]["output"]["type"] = CONNECT_OUTPUT_TYPE_DOCKER
            cluster_dict["spec"]["build"]["output"]["image"] = connect_properties.get(
                SpecialTexts.CONNECT_OUTPUT_IMAGE).data
            cluster_dict["spec"]["build"]["output"]["pushSecret"] = connect_properties.get(
                SpecialTexts.CONNECT_OUTPUT_PUSH_SECRET).data

            cluster_dict["spec"]["build"]["plugins"] = []

            for i, plugin_url in enumerate(
                    get_list_by_split_string(connect_properties.get(SpecialTexts.CONNECT_PLUGIN_URL).data,
                                             COMMA), start=1):
                plugin_dict = {"name": f"connector-{i}", "artifacts": [{"type": "tgz", "url": plugin_url}]}

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
                is_confirmed = click.confirm(Messages.CLUSTER_SAVE_CONFIRMATION)
            if is_confirmed:
                os.system(
                    Kubectl().create().from_file("{cluster_temp_file_path}").namespace(namespace).build().format(
                        cluster_temp_file_path=cluster_temp_file.name))
            cluster_temp_file.close()
