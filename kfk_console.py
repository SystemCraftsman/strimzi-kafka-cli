import click
import os

from .kfk import kfk
from .kubectl_command_builder import Kubectl


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--topic', help='Topic Name', required=True)
@click.option('--from-beginning', help='Consumes messages from beginning', is_flag=True)
@kfk.command()
def console_consumer(topic, cluster, from_beginning, namespace):
    """The console consumer is a tool that reads data from Kafka and outputs it to standard output."""
    native_command = "bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic {topic} {from_beginning}"
    os.system(
        Kubectl().exec("-it", "{cluster}-kafka-0").container("kafka").namespace(namespace).exec_command(
            native_command).build().format(cluster=cluster, topic=topic,
                                           from_beginning=(from_beginning and '--from-beginning' or '')))


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--topic', help='Topic Name', required=True)
@kfk.command()
def console_producer(topic, cluster, namespace):
    """The console producer is a tool that reads data from standard input and publish it to Kafka."""
    native_command = "bin/kafka-console-producer.sh --broker-list localhost:9092 --topic {topic}"
    os.system(
        Kubectl().exec("-it", "{cluster}-kafka-0").container("kafka").namespace(namespace).exec_command(
            native_command).build().format(cluster=cluster, topic=topic))
