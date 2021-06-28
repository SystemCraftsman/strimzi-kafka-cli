import click
import pkg_resources

from kfk.config import KUBECTL_VERSION, STRIMZI_VERSION


version = f"""CLI Version: {pkg_resources.require("strimzi-kafka-cli")[0].version}
Strimzi Version: {STRIMZI_VERSION}
Kubectl Version: {KUBECTL_VERSION}"""


# @click.option('-v', '--version', help='Prints the version', is_flag=True)
@click.version_option(version=1, message=version)
@click.group(name='kfk')
def kfk():
    """Strimzi Kafka CLI"""


if __name__ == '__main__':
    kfk()
