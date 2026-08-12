from kfk.commands.main import kfk


@kfk.group()
def backup():
    """Backs up and restores Strimzi resources."""
