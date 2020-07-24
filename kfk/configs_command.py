import click
import os
import yaml

from kfk.command import kfk
from kfk import topics_command


@kfk.command()
def configs():
    """Add/Remove entity config for a topic, client, user or broker"""
    os.system("echo 'Not implemented'")