import click

from kfk.dependencies import download_kubectl_if_not_exists


@click.group()
def kfk():
    """Strimzi Kafka CLI"""
    download_kubectl_if_not_exists()


if __name__ == '__main__':
    kfk(prog_name='kfk')
