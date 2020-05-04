import click
import os
from option_extensions import NotRequiredIf, RequiredIf


@click.group()
def kfk():
    """A CLI wrapper for the Strimzi Kafka Operator"""


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--native', help='List details for the given topic natively.', is_flag=True, cls=RequiredIf, required_if='describe')
@click.option('--describe', help='List details for the given topic.', is_flag=True)
@click.option('--replication-factor', help='The replication factor for each partition in the topic being created.', cls=RequiredIf, required_if='create')
@click.option('--partitions', help='The number of partitions for the topic being created or altered ', cls=RequiredIf, required_if='create')
@click.option('--create', help='Create a new topic.', is_flag=True)
@click.option('--list', help='List all available topics.', is_flag=True)
@click.option('--topic', help='Topic Name', required=True, cls=NotRequiredIf, not_required_if='list')
@kfk.command()
def topics(topic, list, create, partitions, replication_factor, describe, native, cluster, namespace):
    """The kafka topic(s) to be created, altered or described. """
    if list:
        os.system('kubectl get kafkatopics -l strimzi.io/cluster={} -n {}'.format(cluster, namespace))
    elif create:
        os.system('kubectl exec -it {}-kafka-0 -c kafka -n {} -- bin/kafka-topics.sh --bootstrap-server '
                  'localhost:9092 --create --topic {} --partitions {} --replication-factor {}'.format(cluster, namespace, topic, partitions, replication_factor))
    elif describe:
        if native:
            print("TODO")
        else:
            os.system('kubectl describe kafkatopics {} -l strimzi.io/cluster={} -n {}'.format(topic, cluster, namespace))


@click.option('--cluster', help='Cluster Name', required=True, cls=NotRequiredIf, not_required_if='list')
@click.option('--list', help='List all available clusters.', is_flag=True)
@click.option('-n', '--namespace', help='Namespace to use', default='default')
@kfk.command()
def clusters(cluster, list, namespace):
    """The kafka cluster(s) to be created, altered or described. """
    if list:
        os.system('kubectl get kafkas -n {}'.format(namespace))
    else:
        os.system('kubectl get kafkas {} -n {}'.format(cluster, namespace))


if __name__ == '__main__':
    kfk(prog_name='kfk')
