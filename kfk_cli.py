import click
import os
import io
import wget
import ssl
import tarfile
import yaml

from pathlib import Path
from option_extensions import NotRequiredIf, RequiredIf, Mutex

ssl._create_default_https_context = ssl._create_unverified_context

BASE_PATH = str(Path.home())
STRIMZI_VERSION = "0.18.0"
STRIMZI_PATH = BASE_PATH + "/strimzi-{version}"
STRIMZI_RELEASE_URL = "https://github.com/strimzi/strimzi-kafka-operator/releases/download/{version}/strimzi-{version}.tar.gz"


@click.group()
def kfk():
    """A CLI wrapper for the Strimzi Kafka Operator"""


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--delete-config', help='A topic configuration override to be removed for an existing topic', multiple=True)
@click.option('--config', help='A topic configuration override for the topic being created or altered.', multiple=True)
@click.option('--alter', help='Alter the number of partitions, replica assignment, and/or configuration for the topic.',
              is_flag=True)
@click.option('--native', help='List details for the given topic natively.', is_flag=True, cls=RequiredIf,
              required_if='describe')
@click.option('--describe', help='List details for the given topic.', is_flag=True)
@click.option('--replication-factor', help='The replication factor for each partition in the topic being created.',
              cls=RequiredIf, required_if='create')
@click.option('--partitions', help='The number of partitions for the topic being created or altered ', cls=RequiredIf,
              required_if='create')
@click.option('--create', help='Create a new topic.', is_flag=True)
@click.option('--list', help='List all available topics.', is_flag=True)
@click.option('--topic', help='Topic Name', required=True, cls=NotRequiredIf, not_required_if='list')
@kfk.command()
def topics(topic, list, create, partitions, replication_factor, describe, native, alter, config, delete_config, cluster, namespace):
    """The kafka topic(s) to be created, altered or described. """
    if list:
        os.system('kubectl get kafkatopics -l strimzi.io/cluster={cluster} -n {namespace}'.format(cluster=cluster,
                                                                                                  namespace=namespace))
    elif create:
        download_strimzi_if_not_exists()

        with open(r'{strimzi_path}/examples/topic/kafka-topic.yaml'.format(strimzi_path=STRIMZI_PATH).format(
                version=STRIMZI_VERSION)) as file:
            topic_dict = yaml.full_load(file)

            topic_dict["metadata"]["name"] = topic
            topic_dict["spec"]["partitions"] = int(partitions)
            topic_dict["spec"]["replicas"] = int(replication_factor)

            add_topic_config(config, topic_dict)

            topic_yaml = yaml.dump(topic_dict)
            os.system(
                'echo "{topic_yaml}" | kubectl create -f -'.format(strimzi_path=STRIMZI_PATH, topic_yaml=topic_yaml))

    elif describe:
        if native:
            os.system(
                'kubectl exec -it {cluster}-kafka-0 -c kafka -n {namespace} -- bin/kafka-topics.sh --bootstrap-server '
                'localhost:9092 --describe --topic {topic} '.format(cluster=cluster, namespace=namespace, topic=topic))
        else:
            topic_exists = topic in os.popen(
                'kubectl get kafkatopics -l strimzi.io/cluster={cluster} -n {namespace}'.format(cluster=cluster,
                                                                                                namespace=namespace)).read()
            if topic_exists:
                os.system(
                    'kubectl describe kafkatopics {topic} -n {namespace}'.format(topic=topic, namespace=namespace))

    elif alter:
        download_strimzi_if_not_exists()

        topic_exists = topic in os.popen(
            'kubectl get kafkatopics -l strimzi.io/cluster={cluster} -n {namespace}'.format(cluster=cluster,
                                                                                            namespace=namespace)).read()
        if topic_exists:
            topic_yaml = os.popen(
                'kubectl get kafkatopics {topic} -n {namespace} -o yaml'.format(topic=topic, namespace=namespace)).read()

            file = io.StringIO(topic_yaml)
            topic_dict = yaml.full_load(file)

            topic_dict["spec"]["partitions"] = int(partitions)
            topic_dict["spec"]["replicas"] = int(replication_factor)

            if "annotations" in topic_dict["metadata"]:
                del topic_dict["metadata"]["annotations"]["kubectl.kubernetes.io/last-applied-configuration"]

            add_topic_config(config, topic_dict)
            delete_topic_config(delete_config, topic_dict)

            topic_yaml = yaml.dump(topic_dict)
            print(topic_yaml)
            os.system(
                'echo "{topic_yaml}" | kubectl apply -f -'.format(strimzi_path=STRIMZI_PATH, topic_yaml=topic_yaml))


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('--cluster', help='Cluster Name', required=True, cls=NotRequiredIf, not_required_if='list')
@click.option('--list', help='List all available clusters.', required=True, is_flag=True)
@kfk.command()
def clusters(cluster, list, namespace):
    """The kafka cluster(s) to be created, altered or described. """
    if list:
        os.system('kubectl get kafkas -n {namespace}'.format(namespace=namespace))
    else:
        os.system('kubectl get kafkas {cluster} -n {namespace}'.format(cluster=cluster, namespace=namespace))


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--topic', help='Topic Name', required=True)
@click.option('--from-beginning', help='kfk', is_flag=True)
@kfk.command()
def console_consumer(topic, cluster, from_beginning, namespace):
    os.system(
        'kubectl exec -it {cluster}-kafka-0 -c kafka -n {namespace} -- bin/kafka-console-consumer.sh --bootstrap-server '
        'localhost:9092 --topic {topic} '.format(cluster=cluster, namespace=namespace, topic=topic))


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--topic', help='Topic Name', required=True)
@kfk.command()
def console_producer(topic, cluster, namespace):
    os.system(
        'kubectl exec -it {cluster}-kafka-0 -c kafka -n {namespace} -- bin/kafka-console-producer.sh --broker-list '
        'localhost:9092 --topic {topic} '.format(cluster=cluster, namespace=namespace, topic=topic))


@kfk.command()
def configs():
    print("Not implemented")


def add_topic_config(config, topic_dict):
    if type(config) is tuple:
        for config_str in config:
            config_arr = config_str.split('=')
            topic_dict["spec"]["config"][config_arr[0]] = config_arr[1]


def delete_topic_config(delete_config, topic_dict):
    if type(delete_config) is tuple:
        for delete_config_str in delete_config:
            if delete_config_str in topic_dict["spec"]["config"]:
                del topic_dict["spec"]["config"][delete_config_str]


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


if __name__ == '__main__':
    kfk(prog_name='kfk')
