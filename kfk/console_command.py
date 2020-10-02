import click
import os
import ntpath

from kfk.command import kfk
from kfk.kubectl_command_builder import Kubectl
from kfk.config import *
from kfk.commons import *
from kfk.constants import *


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--from-beginning', help='Consumes messages from beginning', is_flag=True)
@click.option('--consumer.config', 'consumer_config', help='Consumer config properties file.')
@click.option('--topic', help='Topic Name', required=True)
@kfk.command()
def console_consumer(topic, consumer_config, from_beginning, cluster, namespace):
    """The console consumer is a tool that reads data from Kafka and outputs it to standard output."""
    native_command = "bin/kafka-console-consumer.sh --bootstrap-server {cluster}-kafka-brokers:{port} --topic {" \
                     "topic} {from_beginning}"
    pod = cluster + "-kafka-0"
    container = "kafka"
    if consumer_config is not None:
        native_command = apply_client_config_from_file(native_command, consumer_config, "--consumer.config",
                                                       container, pod, namespace)
    os.system(
        Kubectl().exec("-it", pod).container(container).namespace(namespace).exec_command(
            native_command).build().format(port=KAFKA_PORT, topic=topic, cluster=cluster,
                                           from_beginning=(from_beginning and '--from-beginning' or '')))


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--producer.config', 'producer_config', help='Producer config properties file.')
@click.option('--topic', help='Topic Name', required=True)
@kfk.command()
def console_producer(topic, producer_config, cluster, namespace):
    """The console producer is a tool that reads data from standard input and publish it to Kafka."""
    native_command = "bin/kafka-console-producer.sh --broker-list {cluster}-kafka-brokers:{port} --topic {topic}"
    pod = cluster + "-kafka-0"
    container = "kafka"
    if producer_config is not None:
        native_command = apply_client_config_from_file(native_command, producer_config, "--producer.config",
                                                       container, pod, namespace)
    os.system(
        Kubectl().exec("-it", pod).container(container).namespace(namespace).exec_command(
            native_command).build().format(port=KAFKA_PORT, topic=topic, cluster=cluster))
