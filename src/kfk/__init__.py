from src.kfk.commands import kfk
from src.kfk.commands.acls import acls
from src.kfk.commands.clusters import clusters
from src.kfk.commands.configs import configs
from src.kfk.commands.connect.clusters import clusters
from src.kfk.commands.connect.connectors import connectors
from src.kfk.commands.console import console_consumer, console_producer
from src.kfk.commands.env import env
from src.kfk.commands.operator import operator
from src.kfk.commands.topics import topics
from src.kfk.commands.users import users
from src.kfk.setup import prepare_resources

if __name__ == "__main__":
    prepare_resources()
