import click

from kfk.commands.main import kfk
from kfk.commons import print_missing_options_for_command, create_temp_file
from kfk.kubectl_command_builder import Kubectl
from kfk.config import *
from kfk.constants import SpecialTexts


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('--uninstall', 'is_uninstall', help='Uninstalls Strimzi Kafka Operator', is_flag=True)
@click.option('--install', 'is_install', help='Installs Strimzi Kafka Operator', is_flag=True)
@kfk.command()
def operator(is_install, is_uninstall, namespace):
    """Installs/Uninstalls Strimzi Kafka Operator"""
    if is_install:
        for directory_name, dirs, files in os.walk("{strimzi_path}/install/cluster-operator/".format(
                strimzi_path=STRIMZI_PATH)):
            for file_name in files:
                file_path = os.path.join(directory_name, file_name)

                if SpecialTexts.OPERATOR_ROLE_BINDING in file_name:
                    with open(file_path) as file:
                        stream = file.read().replace(SpecialTexts.OPERATOR_MY_PROJECT, namespace)
                        temp_file = create_temp_file(stream)
                        file_path = temp_file.name
                os.system(Kubectl().apply().from_file(file_path).namespace(namespace).build())
    elif is_uninstall:
        # TODO: refactor here
        for directory_name, dirs, files in os.walk("{strimzi_path}/install/cluster-operator/".format(
                strimzi_path=STRIMZI_PATH)):
            for file_name in files:
                file_path = os.path.join(directory_name, file_name)

                if SpecialTexts.OPERATOR_ROLE_BINDING in file_name:
                    with open(file_path) as file:
                        stream = file.read().replace(SpecialTexts.OPERATOR_MY_PROJECT, namespace)
                        temp_file = create_temp_file(stream)
                        file_path = temp_file.name
                os.system(Kubectl().delete().from_file(file_path).namespace(namespace).build())
    else:
        print_missing_options_for_command("operator")
