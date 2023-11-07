import os

import click

from kfk.commands.main import kfk
from kfk.commons import create_temp_file, raise_exception_for_missing_options
from kfk.config import STRIMZI_PATH
from kfk.constants import SpecialTexts
from kfk.kubernetes_commons import create_using_yaml, delete_using_yaml


@click.option("-n", "--namespace", help="Namespace to use", required=True)
@click.option(
    "--uninstall",
    "is_uninstall",
    help="Uninstalls Strimzi Kafka Operator",
    is_flag=True,
)
@click.option(
    "--install", "is_install", help="Installs Strimzi Kafka Operator", is_flag=True
)
@kfk.command()
def operator(is_install, is_uninstall, namespace):
    """Installs/Uninstalls Strimzi Kafka Operator."""

    for directory_name, dirs, files in os.walk(
        "{strimzi_path}/install/cluster-operator/".format(strimzi_path=STRIMZI_PATH)
    ):
        for file_name in files:
            file_path = os.path.join(directory_name, file_name)

            if SpecialTexts.OPERATOR_ROLE_BINDING in file_name:
                with open(file_path) as file:
                    stream = file.read().replace(
                        SpecialTexts.OPERATOR_MY_PROJECT, namespace
                    )
                    temp_file = create_temp_file(stream)
                    file_path = temp_file.name
            if is_install:
                create_using_yaml(file_path, namespace)
            elif is_uninstall:
                delete_using_yaml(file_path, namespace)
            else:
                raise_exception_for_missing_options("operator")
                break
