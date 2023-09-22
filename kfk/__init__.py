import importlib.metadata as importlib_metadata

try:
    # This will read version from pyproject.toml
    # hardcode the package name here to avoid errors
    # __name__ is not the same as the package name
    __version__ = importlib_metadata.version("strimzi-kafka-cli")
except importlib_metadata.PackageNotFoundError:
    print("Package not found. Running in development mode.")
    __version__ = "development"

from kfk.commands.acls import acls
from kfk.commands.clusters import clusters
from kfk.commands.configs import configs
from kfk.commands.connect.clusters import clusters as connect_clusters
from kfk.commands.connect.connectors import connectors
from kfk.commands.console import console_consumer, console_producer
from kfk.commands.env import env
from kfk.commands.main import kfk as kfk_main
from kfk.commands.operator import operator
from kfk.commands.topics import topics
from kfk.commands.users import users
