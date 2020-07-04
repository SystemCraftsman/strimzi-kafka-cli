import click
import pkg_resources

from kfk.command import kfk
from kfk.config import KUBECTL_VERSION, STRIMZI_VERSION


@kfk.command()
def version():
    """Prints the version of Strimzi Kafka CLI"""
    version = pkg_resources.require("strimzi-kafka-cli")[0].version
    click.echo("CLI Version: " + version)
    click.echo("Strimzi Version: " + STRIMZI_VERSION)
    click.echo("Kubectl Version: " + KUBECTL_VERSION)
