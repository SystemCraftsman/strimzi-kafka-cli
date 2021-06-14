from kfk.commands.main import kfk


@kfk.group()
def connect():
    """Creates, alters, deletes, describes Kafka Connect cluster(s) or its connectors."""
