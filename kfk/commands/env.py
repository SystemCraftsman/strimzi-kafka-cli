import click
import os

from kfk.commands.main import kfk


@kfk.command()
def env():
    """Prints the environment variable values for Strimzi Kafka CLI"""

    click.echo("STRIMZI_KAFKA_CLI_BASE_PATH: {}".format(os.environ.get('STRIMZI_KAFKA_CLI_BASE_PATH')))
    click.echo("STRIMZI_KAFKA_CLI_STRIMZI_VERSION: {}".format(os.environ.get('STRIMZI_KAFKA_CLI_STRIMZI_VERSION')))
    click.echo("STRIMZI_KAFKA_CLI_STRIMZI_PATH: {}".format(os.environ.get('STRIMZI_KAFKA_CLI_STRIMZI_PATH')))
    click.echo("STRIMZI_KAFKA_CLI_KUBECTL_VERSION: {}".format(os.environ.get('STRIMZI_KAFKA_CLI_KUBECTL_VERSION')))
    click.echo("STRIMZI_KAFKA_CLI_KUBECTL_PATH: {}".format(os.environ.get('STRIMZI_KAFKA_CLI_KUBECTL_PATH')))
