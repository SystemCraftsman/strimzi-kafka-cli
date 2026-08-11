from importlib.metadata import version

import click

from kfk.config import STRIMZI_VERSION

version = f"""CLI Version: {version("strimzi-kafka-cli")}
Strimzi Version: {STRIMZI_VERSION}"""


# @click.option('-v', '--version', help='Prints the version', is_flag=True)
@click.version_option(version=1, message=version)
@click.group(name="kfk", invoke_without_command=True)
@click.pass_context
def kfk(ctx):
    """Strimzi Kafka CLI."""
    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())


if __name__ == "__main__":
    kfk()
