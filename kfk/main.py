from kfk.commands.acls import acls
from kfk.commands.backup.connect import connect as backup_connect
from kfk.commands.backup.kafka import kafka as backup_kafka
from kfk.commands.clusters import clusters
from kfk.commands.configs import configs
from kfk.commands.connect.clusters import clusters
from kfk.commands.connect.connectors import connectors
from kfk.commands.connect.mirror_maker import mirror_maker
from kfk.commands.console import console_consumer, console_producer
from kfk.commands.main import kfk
from kfk.commands.mcp import mcp
from kfk.commands.node_pools import node_pools
from kfk.commands.operator import operator
from kfk.commands.topics import topics
from kfk.commands.users import users
from kfk.setup import setup

setup()
