import click
import os

from kfk.command import kfk
from kfk.option_extensions import NotRequiredIf
from kfk.commons import print_missing_options_for_command, get_resource_as_stream, open_file_in_system_editor, \
    create_temp_file
from kfk.kubectl_command_builder import Kubectl
from kfk.config import *


@click.option('-n', '--namespace', help='Namespace to use')
@click.option('-o', '--output',
              help='Output format. One of: json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath'
                   '|jsonpath-file.')
@click.option('--alter', help='Alter the cluster.', is_flag=True)
@click.option('--delete', help='Delete the cluster.', is_flag=True)
@click.option('--create', help='Create the cluster.', is_flag=True)
@click.option('--describe', help='List details for the given cluster.', is_flag=True)
@click.option('--list', help='List all available clusters.', required=True, is_flag=True)
@click.option('--cluster', help='Cluster Name', required=True, cls=NotRequiredIf, not_required_if=['list'])
@kfk.command()
def clusters(cluster, list, create, describe, delete, alter, output, namespace):
    """The kafka cluster(s) to be created, altered or described. """
    if list:
        os.system(Kubectl().get().kafkas().namespace(namespace).build())
    elif create:
        with open('{strimzi_path}/examples/kafka/kafka-ephemeral.yaml'.format(strimzi_path=STRIMZI_PATH).format(
                version=STRIMZI_VERSION)) as file:
            cluster_temp_file = create_temp_file(file.read())
            open_file_in_system_editor(cluster_temp_file.name)
            is_confirmed = click.confirm("Are you sure you want to create the cluster?")
            if is_confirmed:
                os.system(Kubectl().create().from_file("{cluster_temp_file_path}").namespace(namespace).build().format(
                    cluster_temp_file_path=cluster_temp_file.name))
            cluster_temp_file.close()

    elif describe:
        if output is not None:
            os.system(Kubectl().get().kafkas(cluster).namespace(namespace).output(output).build())
        else:
            os.system(Kubectl().describe().kafkas(cluster).namespace(namespace).build())
    elif delete:
        is_confirmed = click.confirm("Are you sure you want to delete the cluster?")
        if is_confirmed:
            os.system(Kubectl().delete().kafkas(cluster).namespace(namespace).build())
    elif alter:
        os.system(Kubectl().edit().kafkas(cluster).namespace(namespace).build())
    else:
        print_missing_options_for_command("clusters")
