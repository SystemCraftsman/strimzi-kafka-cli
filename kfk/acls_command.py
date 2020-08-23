import click
import os

from kfk.command import kfk
from kfk.option_extensions import NotRequiredIf, RequiredIf
from kfk.kubectl_command_builder import Kubectl
from kfk.commons import print_missing_options_for_command
from kfk import users_command

PRINCIPAL_SPLIT_CHAR = ":"


@click.option('-n', '--namespace', help='Namespace to use.', required=True)
@click.option('-c', '--kafka-cluster', help='Cluster to use.', required=True)
@click.option('--remove', help='Indicates you are trying to remove ACLs.', is_flag=True)
@click.option('--resource-pattern-type',
              help="The type of the resource pattern or <ANY|MATCH|LITERAL|PREFIXED> pattern filter. When adding "
                   "acls, this should be a specific pattern type, e.g. 'literal' or 'prefixed'. (default: literal)",
              default='literal')
@click.option('--deny-host', help='Host which User will not have access. (default: *)', default='*')
@click.option('--allow-host', help='Host which User will have access. (default: *)', default='*')
@click.option('--operation', 'operation_tuple', help='Operation that is being allowed or denied. (default: All)',
              default=["All"], multiple=True)
@click.option('--deny-principal',
              help='principal is in principalType:name format. By default anyone not added through --allow-principal '
                   'is denied access. You only need to use this option as negation to already allowed set.',
              required=True, cls=NotRequiredIf, not_required_if=['list', 'allow_principal'])
@click.option('--allow-principal',
              help='principal is in principalType:name principal format. Note that principalType must be supported '
                   'by the Authorizer being used.', required=True, cls=NotRequiredIf,
              not_required_if=['list', 'deny_principal'])
@click.option('--add', help='Indicates you are trying to add ACLs.', is_flag=True)
@click.option('--group', help='Consumer Group ACLs.')
@click.option('--cluster', help='Cluster ACLs.')
@click.option('--topic', help='Topic ACLs.')
@click.option('--list',
              help='List ACLs for the specified resource, use --topic <topic> or --group <group> or --cluster to '
                   'specify a resource.',
              is_flag=True)
@kfk.command()
def acls(list, topic, cluster, group, add, allow_principal, deny_principal, operation_tuple, allow_host, deny_host,
         resource_pattern_type, remove, kafka_cluster, namespace):
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
    elif add or remove:
        alter(topic, cluster, group, add, remove, allow_principal, deny_principal, operation_tuple, allow_host, deny_host,
              resource_pattern_type, kafka_cluster, namespace)
    else:
        print_missing_options_for_command("acls")


def alter(topic, cluster, group, add, remove, allow_principal, deny_principal, operation_tuple, allow_host, deny_host,
          resource_pattern_type, kafka_cluster, namespace):
    resource_type_dict = get_resource_type_dict(topic, cluster, group)

    if allow_principal:
        type = "allow"
        # TODO: click exception here
        allow_principal_arr = allow_principal.split(PRINCIPAL_SPLIT_CHAR)
        principal_type = allow_principal_arr[0]
        principal_name = allow_principal_arr[1]
        host = allow_host
    else:
        type = "deny"
        # TODO: click exception here
        deny_principal_arr = deny_principal.split(PRINCIPAL_SPLIT_CHAR)
        principal_type = deny_principal_arr[0]
        principal_name = deny_principal_arr[1]
        host = deny_host
    if principal_type == "User":
        for resource_type, resource_name in resource_type_dict.items():
            users_command.alter(principal_name, None, None, add, remove, operation_tuple, host, type,
                                resource_type, resource_name, resource_pattern_type, tuple(), tuple(),
                                kafka_cluster, namespace)


def get_resource_type_dict(topic, cluster, group):
    resource_type_dict = {}

    if topic is not None:
        resource_type_dict["topic"] = topic
    if cluster is not None:
        resource_type_dict["cluster"] = cluster
    if group is not None:
        resource_type_dict["group"] = group

    return resource_type_dict
