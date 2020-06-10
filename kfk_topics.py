import click
import os
import yaml

from .kfk import kfk
from .option_extensions import NotRequiredIf, RequiredIf
from .commons import print_missing_options_for_command, download_strimzi_if_not_exists, \
    delete_last_applied_configuration, resource_exists, get_resource_as_file, add_resource_kv_config, \
    delete_resource_config
from .constants import *
from .kubectl_command_builder import Kubectl


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--delete-config', help='A topic configuration override to be removed for an existing topic',
              multiple=True)
@click.option('--config', help='A topic configuration override for the topic being created or altered.', multiple=True)
@click.option('--alter', help='Alter the number of partitions, replica assignment, and/or configuration of the topic.',
              is_flag=True)
@click.option('--delete', help='Delete a topic.', is_flag=True)
@click.option('--native', help='List details for the given topic natively.', is_flag=True, cls=RequiredIf,
              required_if='describe')
@click.option('-o', '--output',
              help='Output format. One of: json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath'
                   '|jsonpath-file.')
@click.option('--describe', help='List details for the given topic.', is_flag=True)
@click.option('--replication-factor', help='The replication factor for each partition in the topic being created.',
              cls=RequiredIf, required_if='create')
@click.option('--partitions', help='The number of partitions for the topic being created or altered ', cls=RequiredIf,
              required_if='create')
@click.option('--create', help='Create a new topic.', is_flag=True)
@click.option('--list', help='List all available topics.', is_flag=True)
@click.option('--topic', help='Topic Name', required=True, cls=NotRequiredIf, not_required_if='list')
@kfk.command()
def topics(topic, list, create, partitions, replication_factor, describe, output, native, delete, alter, config,
           delete_config, cluster, namespace):
    """The kafka topic(s) to be created, altered or described."""
    if list:
        os.system(
            Kubectl().get().kafkatopics().label("strimzi.io/cluster={cluster}").namespace(namespace).build().format(
                cluster=cluster))
    elif create:
        download_strimzi_if_not_exists()

        with open(r'{strimzi_path}/examples/topic/kafka-topic.yaml'.format(strimzi_path=STRIMZI_PATH).format(
                version=STRIMZI_VERSION)) as file:
            topic_dict = yaml.full_load(file)

            topic_dict["metadata"]["name"] = topic
            topic_dict["spec"]["partitions"] = int(partitions)
            topic_dict["spec"]["replicas"] = int(replication_factor)

            add_resource_kv_config(config, topic_dict)

            topic_yaml = yaml.dump(topic_dict)
            os.system(
                'echo "{topic_yaml}" | '.format(topic_yaml=topic_yaml) + Kubectl().create().from_file("-").namespace(
                    namespace).build())

    elif describe:
        if output is not None:
            if resource_exists("kafkatopics", topic, cluster, namespace):
                os.system(
                    Kubectl().get().kafkatopics(topic).namespace(namespace).output(output).build())
        else:
            if native:
                native_command = "bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic {topic}"
                os.system(
                    Kubectl().exec("-it", "{cluster}-kafka-0").container("kafka").namespace(namespace).exec_command(
                        native_command).build().format(topic=topic, cluster=cluster))
            else:
                if resource_exists("kafkatopics", topic, cluster, namespace):
                    os.system(
                        Kubectl().describe().kafkatopics(topic).namespace(namespace).build())

    elif delete:
        if resource_exists("kafkatopics", topic, cluster, namespace):
            os.system(Kubectl().delete().kafkatopics(topic).namespace(namespace).build())

    elif alter:
        if resource_exists("kafkatopics", topic, cluster, namespace):
            file = get_resource_as_file("kafkatopics", topic, namespace)
            topic_dict = yaml.full_load(file)

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
            os.system(
                'echo "{topic_yaml}" | '.format(topic_yaml=topic_yaml) + Kubectl().apply().from_file("-").namespace(
                    namespace).build())
    else:
        print_missing_options_for_command("topics")
