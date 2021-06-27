import click
import os
import yaml

from kfk.commands.main import kfk
from kfk.option_extensions import NotRequiredIf
from kfk.commons import *
from kfk.kubectl_command_builder import Kubectl
from kfk.config import *
from kfk.messages import Messages


@click.option('-y', '--yes', 'is_yes', help='"Yes" confirmation', is_flag=True)
@click.option('-n', '--namespace', help='Namespace to use')
@click.option('--delete-config', help='A cluster configuration override to be removed for an existing cluster',
              multiple=True)
@click.option('--config', help='A cluster configuration override for the cluster being altered.',
              multiple=True)
@click.option('--alter', 'is_alter', help='Alters the Kafka cluster.', is_flag=True)
@click.option('--delete', 'is_delete', help='Deletes the Kafka cluster.', is_flag=True)
@click.option('--zk-replicas', help='The number of zookeeper replicas for the cluster.', type=int)
@click.option('--replicas', help='The number of broker replicas for the cluster.', type=int)
@click.option('--create', 'is_create', help='Creates a Kafka cluster.', is_flag=True)
@click.option('--describe', 'is_describe', help='Lists details for the given cluster.', is_flag=True)
@click.option('-o', '--output',
              help='Output format. One of: json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath'
                   '|jsonpath-file.')
@click.option('--list', 'is_list', help='List all available clusters.', required=True, is_flag=True)
@click.option('--cluster', help='Cluster Name', required=True, cls=NotRequiredIf, options=['is_list'])
@kfk.command()
def clusters(cluster, is_list, is_create, replicas, zk_replicas, is_describe, is_delete, is_alter, config,
             delete_config, output, namespace, is_yes):
    """Creates, alters, deletes, describes Kafka cluster(s)."""
    if is_list:
        list(namespace)
    elif is_create:
        create(cluster, replicas, zk_replicas, config, namespace, is_yes)
    elif is_describe:
        describe(cluster, output, namespace)
    elif is_delete:
        delete(cluster, namespace, is_yes)
    elif is_alter:
        alter(cluster, replicas, zk_replicas, config, delete_config, namespace)
    else:
        print_missing_options_for_command("clusters")


def list(namespace):
    os.system(Kubectl().get().kafkas().namespace(namespace).build())


def create(cluster, replicas, zk_replicas, config, namespace, is_yes):
    with open('{strimzi_path}/examples/kafka/kafka-ephemeral.yaml'.format(strimzi_path=STRIMZI_PATH).format(
            version=STRIMZI_VERSION)) as file:
        stream = file.read()

        cluster_dict = yaml.full_load(stream)

        cluster_dict["metadata"]["name"] = cluster

        _update_replicas(replicas, zk_replicas, cluster_dict)

        _add_config_if_provided(config, cluster_dict)

        cluster_yaml = yaml.dump(cluster_dict)

        cluster_temp_file = create_temp_file(cluster_yaml)

        if is_yes:
            is_confirmed = True
        else:
            open_file_in_system_editor(cluster_temp_file.name)
            is_confirmed = click.confirm(Messages.CLUSTER_CREATE_CONFIRMATION)
        if is_confirmed:
            os.system(Kubectl().create().from_file("{cluster_temp_file_path}").namespace(namespace).build().format(
                cluster_temp_file_path=cluster_temp_file.name))
        cluster_temp_file.close()


def describe(cluster, output, namespace):
    if output is not None:
        os.system(Kubectl().get().kafkas(cluster).namespace(namespace).output(output).build())
    else:
        os.system(Kubectl().describe().kafkas(cluster).namespace(namespace).build())


def delete(cluster, namespace, is_yes):
    if is_yes:
        is_confirmed = True
    else:
        is_confirmed = click.confirm(Messages.CLUSTER_DELETE_CONFIRMATION)
    if is_confirmed:
        os.system(Kubectl().delete().kafkas(cluster).namespace(namespace).build())


def alter(cluster, replicas, zk_replicas, config, delete_config, namespace):
    if len(config) > 0 or len(delete_config) > 0 or replicas is not None or zk_replicas is not None:
        stream = get_resource_as_stream("kafkas", resource_name=cluster, namespace=namespace)
        cluster_dict = yaml.full_load(stream)

        delete_last_applied_configuration(cluster_dict)

        _update_replicas(replicas, zk_replicas, cluster_dict)

        _add_config_if_provided(config, cluster_dict)

        if len(delete_config) > 0:
            if cluster_dict["spec"]["kafka"].get("config") is not None:
                delete_resource_config(delete_config, cluster_dict["spec"]["kafka"]["config"])

        cluster_yaml = yaml.dump(cluster_dict)
        cluster_temp_file = create_temp_file(cluster_yaml)
        os.system(
            Kubectl().apply().from_file("{cluster_temp_file_path}").namespace(namespace).build().format(
                cluster_temp_file_path=cluster_temp_file.name))
        cluster_temp_file.close()
    else:
        os.system(Kubectl().edit().kafkas(cluster).namespace(namespace).build())


def _update_replicas(replicas, zk_replicas, cluster_dict):
    if replicas is not None:
        cluster_dict["spec"]["kafka"]["replicas"] = int(replicas)
        min_insync_replicas = 1
        if replicas > 1:
            min_insync_replicas = replicas - 1
        cluster_dict["spec"]["kafka"]["config"]["offsets.topic.replication.factor"] = int(replicas)
        cluster_dict["spec"]["kafka"]["config"]["transaction.state.log.replication.factor"] = int(replicas)
        cluster_dict["spec"]["kafka"]["config"]["transaction.state.log.min.isr"] = min_insync_replicas

    if zk_replicas is not None:
        cluster_dict["spec"]["zookeeper"]["replicas"] = int(zk_replicas)


def _add_config_if_provided(config, cluster_dict):
    if len(config) > 0:
        if cluster_dict["spec"]["kafka"].get("config") is None:
            cluster_dict["spec"]["kafka"]["config"] = {}
        add_kv_config_to_resource(config, cluster_dict["spec"]["kafka"]["config"])
