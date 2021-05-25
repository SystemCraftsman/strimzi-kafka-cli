import click
import os
import yaml

from kfk.commands.main import kfk
from kfk.commons import *
from kfk.config import *
from kfk.messages import Errors
from kfk.constants import *
from jproperties import Properties

CONNECT_SKIPPED_PROPERTIES = (
    SpecialTexts.CONNECT_BOOTSTRAP_SERVERS, SpecialTexts.CONNECT_OUTPUT_IMAGE, SpecialTexts.CONNECT_PLUGIN_URL,
    SpecialTexts.CONNECT_PLUGIN_PATH)


# TODO enter command explanations
@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.argument('config_files', nargs=-1, type=click.File('r'))
@click.option('--replica-count', help='', type=int)
@click.option('--cluster', help='Connect cluster name')
@click.option('--create', 'is_create', help='Create a new connect cluster.', is_flag=True)
@kfk.command()
def connect(is_create, cluster, replica_count, config_files, namespace):
    """Creates, alters, deletes, describes Kafka connect cluster(s) or connectors."""
    if is_create:
        create(cluster, replica_count, config_files, namespace)

    else:
        print_missing_options_for_command("connect")


def create(cluster, replica_count, config_files, namespace):
    if cluster is not None:
        if len(config_files) == 0:
            raise click.ClickException(Errors.CONFIG_FILE_SHOULD_BE_PROVIDED)

        with open('{strimzi_path}/examples/connect/kafka-connect.yaml'.format(strimzi_path=STRIMZI_PATH).format(
                version=STRIMZI_VERSION)) as file:
            cluster_dict = yaml.full_load(file)

            connect_properties = Properties()
            connect_properties.load(config_files[0].read())

            cluster_dict["metadata"]["name"] = cluster
            cluster_dict["spec"]["bootstrapServers"] = connect_properties.get(SpecialTexts.CONNECT_BOOTSTRAP_SERVERS).data
            cluster_dict["spec"]["tls"] = {}

            if replica_count is not None:
                cluster_dict["spec"]["replicas"] = replica_count

            cluster_dict["spec"]["config"] = {}

            for item in connect_properties.items():
                if item[0] not in CONNECT_SKIPPED_PROPERTIES:
                    cluster_dict["spec"]["config"][item[0]] = item[1].data

            cluster_yaml = yaml.dump(cluster_dict)
            cluster_temp_file = create_temp_file(cluster_yaml)
            os.system(
                Kubectl().create().from_file("{cluster_temp_file_path}").namespace(namespace).build().format(
                    cluster_temp_file_path=cluster_temp_file.name))
            cluster_temp_file.close()
