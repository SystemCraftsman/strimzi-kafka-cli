import click

from kfk.command import kfk
from kfk.commons import print_missing_options_for_command, create_temp_file
from kfk.kubectl_command_builder import Kubectl
from kfk.config import *


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('--uninstall', help='Installs Strimzi Kafka Operator', is_flag=True)
@click.option('--install', help='Installs Strimzi Kafka Operator', is_flag=True)
@kfk.command()
def operator(install, uninstall, namespace):
    """Install/Uninstall Strimzi Kafka Operator"""
    if install:
        for directory_name, dirs, files in os.walk("{strimzi_path}/install/cluster-operator/".format(
                strimzi_path=STRIMZI_PATH)):
            for file_name in files:
                file_path = os.path.join(directory_name, file_name)

                if "RoleBinding" in file_name:
                    with open(file_path) as file:
                        stream = file.read().replace("myproject", namespace)
                        temp_file = create_temp_file(stream)
                        file_path = temp_file.name

                os.system(
                    Kubectl().apply().from_file(file_path).namespace(namespace).build())
    elif uninstall:
        click.echo("Not implemented")
    else:
        print_missing_options_for_command("operator")
