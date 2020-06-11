import click


@click.group()
def kfk():
    """Strimzi Kafka CLI"""


if __name__ == '__main__':
    kfk(prog_name='kfk')
