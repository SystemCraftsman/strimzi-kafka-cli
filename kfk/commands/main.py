import click


@click.group(name='kfk')
def kfk():
    """Strimzi Kafka CLI"""


if __name__ == '__main__':
    kfk()
