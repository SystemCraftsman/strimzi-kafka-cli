import click
import os
from option_extensions import NotRequiredIf, RequiredIf, Mutex


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
        #TODO: use the normal method instead of the native one. how will you do it? need a template or sth like that!
        os.system('kubectl exec -it {}-kafka-0 -c kafka -n {} -- bin/kafka-topics.sh --bootstrap-server '
                  'localhost:9092 --create --topic {} --partitions {} --replication-factor {}'.format(cluster, namespace, topic, partitions, replication_factor))
    elif describe:
        if native:
            os.system('kubectl exec -it {}-kafka-0 -c kafka -n {} -- bin/kafka-topics.sh --bootstrap-server '
                      'localhost:9092 --describe --topic {} '.format(cluster, namespace, topic))
        else:
            topic_exists = topic in os.popen('kubectl get kafkatopics -l strimzi.io/cluster={} -n {}'.format(cluster, namespace)).read()
            if topic_exists:
                os.system('kubectl describe kafkatopics {} -n {}'.format(topic, namespace))


@click.option('--cluster', help='Cluster Name', required=True, cls=NotRequiredIf, not_required_if='list')
@click.option('--list', help='List all available clusters.', required=True, is_flag=True)
@click.option('-n', '--namespace', help='Namespace to use', default='default')
@kfk.command()
def clusters(cluster, list, namespace):
    """The kafka cluster(s) to be created, altered or described. """
    if list:
        os.system('kubectl get kafkas -n {}'.format(namespace))
    else:
        os.system('kubectl get kafkas {} -n {}'.format(cluster, namespace))


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--topic', help='Topic Name', required=True)
@click.option('--from-beginning', help='kfk', is_flag=True)
@kfk.command()
def console_consumer(topic, cluster, from_beginning, namespace):
    os.system('kubectl exec -it {}-kafka-0 -c kafka -n {} -- bin/kafka-console-consumer.sh --bootstrap-server '
              'localhost:9092 --topic {} '.format(cluster, namespace, topic))


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--topic', help='Topic Name', required=True)
@kfk.command()
def console_producer(topic, cluster, namespace):
    os.system('kubectl exec -it {}-kafka-0 -c kafka -n {} -- bin/kafka-console-producer.sh --broker-list '
              'localhost:9092 --topic {} '.format(cluster, namespace, topic))

@kfk.command()
def configs():
    print("Not implemented")


if __name__ == '__main__':
    kfk(prog_name='kfk')
