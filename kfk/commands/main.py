import click

from kfk import __version__
from kfk.config import KUBECTL_VERSION, STRIMZI_VERSION

version = f"""CLI Version: {__version__}
Strimzi Version: {STRIMZI_VERSION}
Kubectl Version: {KUBECTL_VERSION}"""


@click.version_option(version="1", message=version)
@click.group(name="kfk", no_args_is_help=True)
def kfk():
    """Strimzi Kafka CLI"""


if __name__ == "__main__":
    kfk()
