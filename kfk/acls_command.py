import click
import os

from kfk.command import kfk
from kfk.option_extensions import NotRequiredIf, RequiredIf
from kfk.kubectl_command_builder import Kubectl
from kfk.commons import print_missing_options_for_command
from kfk import users_command


@click.option('-n', '--namespace', help='Namespace to use.', required=True)
@click.option('-c', '--kafka-cluster', help='Cluster to use.', required=True)
@click.option('--remove', help='Indicates you are trying to remove ACLs.', is_flag=True)
@click.option('--allow-principal',
              help='principal is in principalType:name principal format. Note that principalType must be supported '
                   'by the Authorizer being used.', cls=RequiredIf, required_if='add')
@click.option('--add', help='Indicates you are trying to add ACLs.', is_flag=True)
@click.option('--group', help='Consumer Group ACLs.')
@click.option('--cluster', help='Cluster ACLs.')
@click.option('--topic', help='Topic ACLs.')
@click.option('--list',
              help='List ACLs for the specified resource, use --topic <topic> or --group <group> or --cluster to '
                   'specify a resource.',
              is_flag=True)
@kfk.command()
def acls(list, topic, cluster, group, add, allow_principal, remove, kafka_cluster, namespace):
    """This tool helps to manage ACLs on Kafka."""
    if list:
        native_command = "bin/kafka-acls.sh --authorizer-properties zookeeper.connect=localhost:12181 --list {topic}" \
                         "{cluster} {group}"
        os.system(
            Kubectl().exec("-it", "{kafka_cluster}-zookeeper-0").container("zookeeper").namespace(
                namespace).exec_command(
                native_command).build().format(kafka_cluster=kafka_cluster, topic=(topic and '--topic ' + topic or ''),
                                               cluster=(cluster and '--cluster ' + cluster or ''),
                                               group=(group and '--group ' + group or '')))
    elif add:
        # TODO: exception here
        allow_principal_arr = allow_principal.split(":")
        principal_type = allow_principal_arr[0]
        principal_name = allow_principal_arr[1]
        if principal_type == "User":
            users_command.alter_option(principal_name, None, tuple(), tuple(), kafka_cluster, namespace)
    elif remove:
        print("Not implemented")
    else:
        print_missing_options_for_command("acls")
