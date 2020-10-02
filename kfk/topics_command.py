import click
import os
import yaml

from kfk.command import kfk
from kfk.option_extensions import NotRequiredIf, RequiredIf
from kfk.commons import *
from kfk.config import *
from kfk.kubectl_command_builder import Kubectl
from kfk.constants import *


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--delete-config', help='A topic configuration override to be removed for an existing topic',
              multiple=True)
@click.option('--config', help='A topic configuration override for the topic being created or altered.', multiple=True)
@click.option('--alter', 'is_alter',
              help='Alter the number of partitions, replica assignment, and/or configuration of the topic.',
              is_flag=True)
@click.option('--delete', 'is_delete', help='Delete a topic.', is_flag=True)
@click.option('--command-config',
              help='Property file containing configs to be config property file passed to Admin Client.')
@click.option('--native', help='List details for the given topic natively.', is_flag=True, cls=RequiredIf,
              required_if=['is_describe'])
@click.option('-o', '--output',
              help='Output format. One of: json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath'
                   '|jsonpath-file.')
@click.option('--describe', 'is_describe', help='List details for the given topic.', is_flag=True)
@click.option('--replication-factor', help='The replication factor for each partition in the topic being created.',
              cls=RequiredIf, required_if=['is_create'], type=int)
@click.option('--partitions', help='The number of partitions for the topic being created or altered ', cls=RequiredIf,
              required_if=['is_create'], type=int)
@click.option('--create', 'is_create', help='Create a new topic.', is_flag=True)
@click.option('--list', 'is_list', help='List all available topics.', is_flag=True)
@click.option('--topic', help='Topic Name', required=True, cls=NotRequiredIf, not_required_if=['is_list'])
@kfk.command()
def topics(topic, is_list, is_create, partitions, replication_factor, is_describe, output, native, command_config,
           is_delete, is_alter, config, delete_config, cluster, namespace):
    """The kafka topic(s) to be created, altered or described."""
    if is_list:
        list(cluster, namespace)
    elif is_create:
        create(topic, partitions, replication_factor, config, cluster, namespace)
    elif is_describe:
        describe(topic, output, native, command_config, cluster, namespace)
    elif is_delete:
        delete(topic, cluster, namespace)
    elif is_alter:
        alter(topic, partitions, replication_factor, config, delete_config, cluster, namespace)
    else:
        print_missing_options_for_command("topics")


def list(cluster, namespace):
    os.system(
        Kubectl().get().kafkatopics().label("strimzi.io/cluster={cluster}").namespace(namespace).build().format(
            cluster=cluster))


def create(topic, partitions, replication_factor, config, cluster, namespace):
    with open('{strimzi_path}/examples/topic/kafka-topic.yaml'.format(strimzi_path=STRIMZI_PATH).format(
            version=STRIMZI_VERSION)) as file:
        topic_dict = yaml.full_load(file)

        topic_dict["metadata"]["name"] = topic
        topic_dict["metadata"]["labels"]["strimzi.io/cluster"] = cluster
        topic_dict["spec"]["partitions"] = int(partitions)
        topic_dict["spec"]["replicas"] = int(replication_factor)

        if len(config) > 0:
            if topic_dict["spec"].get("config") is None:
                topic_dict["spec"]["config"] = {}
            add_resource_kv_config(config, topic_dict["spec"]["config"])

        topic_yaml = yaml.dump(topic_dict)
        topic_temp_file = create_temp_file(topic_yaml)
        os.system(
            Kubectl().create().from_file("{topic_temp_file_path}").namespace(namespace).build().format(
                topic_temp_file_path=topic_temp_file.name))
        topic_temp_file.close()


def describe(topic, output, native, command_config, cluster, namespace):
    if output is not None:
        if resource_exists("kafkatopics", topic, cluster, namespace):
            os.system(
                Kubectl().get().kafkatopics(topic).namespace(namespace).output(output).build())
    else:
        if native:
            native_command = "bin/kafka-topics.sh --bootstrap-server {cluster}-kafka-brokers:{port} --describe " \
                             "--topic {topic}"
            pod = cluster + "-kafka-0"
            container = "kafka"
            if command_config is not None:
                native_command = apply_client_config_from_file(native_command, command_config, "--command-config",
                                                               container, pod, namespace)
            os.system(
                Kubectl().exec("-it", pod).container(container).namespace(namespace).exec_command(
                    native_command).build().format(port=KAFKA_PORT, topic=topic, cluster=cluster))
        else:
            if resource_exists("kafkatopics", topic, cluster, namespace):
                os.system(
                    Kubectl().describe().kafkatopics(topic).namespace(namespace).build())


def delete(topic, cluster, namespace):
    if resource_exists("kafkatopics", topic, cluster, namespace):
        os.system(Kubectl().delete().kafkatopics(topic).namespace(namespace).build())


def alter(topic, partitions, replication_factor, config, delete_config, cluster, namespace):
    if resource_exists("kafkatopics", topic, cluster, namespace):
        stream = get_resource_as_stream("kafkatopics", topic, namespace)
        topic_dict = yaml.full_load(stream)

        if partitions is not None:
            topic_dict["spec"]["partitions"] = int(partitions)

        if replication_factor is not None:
            topic_dict["spec"]["replicas"] = int(replication_factor)

        delete_last_applied_configuration(topic_dict)

        if len(config) > 0:
            if topic_dict["spec"].get("config") is None:
                topic_dict["spec"]["config"] = {}
            add_resource_kv_config(config, topic_dict["spec"]["config"])

        if len(delete_config) > 0:
            if topic_dict["spec"].get("config") is not None:
                delete_resource_config(delete_config, topic_dict["spec"]["config"])

        topic_yaml = yaml.dump(topic_dict)
        topic_temp_file = create_temp_file(topic_yaml)
        os.system(
            Kubectl().apply().from_file("{topic_temp_file_path}").namespace(namespace).build().format(
                topic_temp_file_path=topic_temp_file.name))
        topic_temp_file.close()
    else:
        print_resource_not_found_msg(cluster, namespace)
