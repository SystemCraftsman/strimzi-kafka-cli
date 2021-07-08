import click
import os
import yaml

from kfk.commands.main import kfk
from kfk.option_extensions import NotRequiredIf, RequiredIf
from kfk.commons import *
from kfk.config import *
from kfk.kubectl_command_builder import Kubectl
from kfk.utils import snake_to_camel_case


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--delete-quota', 'delete_quota_tuple', help='User quotas to be removed.', multiple=True)
@click.option('--quota', 'quota_tuple', help='User\'s network and CPU utilization quotas in the Kafka cluster.',
              multiple=True)
@click.option('--resource-pattern-type',
              help="The type of the resource pattern or <ANY|MATCH|LITERAL|PREFIXED> pattern filter. When adding "
                   "acls, this should be a specific pattern type, e.g. 'literal' or 'prefixed'. (default: literal)",
              default='literal')
@click.option('--resource-name', help='ACL resource name.', cls=RequiredIf, options=['add_acl', 'delete_acl'])
@click.option('--resource-type', help='ACL resource type.',
              type=click.Choice(['topic', 'group', 'cluster'], case_sensitive=True), cls=RequiredIf,
              options=['add_acl', 'delete_acl'])
@click.option('--type', help='Operation type for ACL. (default: allow)',
              type=click.Choice(['allow', 'deny'], case_sensitive=True), default='allow')
@click.option('--host', help='Host which User will have access. (default: *)', default='*')
@click.option('--operation', 'operation_tuple', help='Operation that is being allowed or denied. (default: All)',
              default=["All"], multiple=True)
@click.option('--delete-acl', help='Delete ACL of User', is_flag=True)
@click.option('--add-acl', help='Add ACL to User', is_flag=True)
@click.option('--authorization-type', help='Authorization type for user',
              type=click.Choice(['none', 'simple'], case_sensitive=True))
@click.option('--alter', 'is_alter', help='Alter authentication-type, quotas, etc. of the user.', is_flag=True)
@click.option('--delete', 'is_delete', help='Delete a user.', is_flag=True)
@click.option('-o', '--output',
              help='Output format. One of: json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath'
                   '|jsonpath-file.')
@click.option('--describe', 'is_describe', help='List details for the given user.', is_flag=True)
@click.option('--authentication-type', help='Authentication type for user',
              type=click.Choice(['tls', 'scram-sha-512'], case_sensitive=True), cls=RequiredIf,
              options=['is_create'])
@click.option('--create', 'is_create', help='Create a new user.', is_flag=True)
@click.option('--list', 'is_list', help='List all available users.', is_flag=True)
@click.option('--user', help='User Name', required=True, cls=NotRequiredIf, options=['is_list'])
@kfk.command()
def users(user, is_list, is_create, authentication_type, is_describe, output, is_delete, is_alter, authorization_type,
          add_acl, delete_acl, operation_tuple, host, type, resource_type, resource_name, resource_pattern_type,
          quota_tuple, delete_quota_tuple, cluster, namespace):
    """Creates, alters, deletes, describes Kafka users(s)."""
    if is_list:
        list(cluster, namespace)
    elif is_create:
        create(user, authentication_type, quota_tuple, cluster, namespace)
    elif is_describe:
        describe(user, output, cluster, namespace)
    elif is_delete:
        delete(cluster, namespace, user)
    elif is_alter:
        alter(user, authentication_type, authorization_type, add_acl, delete_acl, operation_tuple, host, type,
              resource_type, resource_name, resource_pattern_type, quota_tuple, delete_quota_tuple, cluster, namespace)
    else:
        print_missing_options_for_command("users")


def list(cluster, namespace):
    os.system(
        Kubectl().get().kafkausers().label("strimzi.io/cluster={cluster}").namespace(namespace).build().format(
            cluster=cluster))


def create(user, authentication_type, quota, cluster, namespace):
    with open('{strimzi_path}/examples/user/kafka-user.yaml'.format(strimzi_path=STRIMZI_PATH).format(
            version=STRIMZI_VERSION)) as file:
        user_dict = yaml.full_load(file)

        user_dict["metadata"]["name"] = user
        user_dict["metadata"]["labels"]["strimzi.io/cluster"] = cluster

        user_dict["spec"]["authentication"]["type"] = authentication_type
        user_dict["spec"].pop("authorization")

        if len(quota) > 0:
            if user_dict["spec"].get("quotas") is None:
                user_dict["spec"]["quotas"] = {}
            add_kv_config_to_resource(quota, user_dict["spec"]["quotas"])

        user_yaml = yaml.dump(user_dict)
        user_temp_file = create_temp_file(user_yaml)

        os.system(
            Kubectl().create().from_file("{user_temp_file_path}").namespace(namespace).build().format(
                user_temp_file_path=user_temp_file.name))

        user_temp_file.close()


def describe(user, output, cluster, namespace):
    if output is not None:
        os.system(Kubectl().get().kafkausers(user).namespace(namespace).output(output).build())
    else:
        os.system(Kubectl().describe().kafkausers(user).namespace(namespace).build())


def delete(cluster, namespace, user):
    os.system(Kubectl().delete().kafkausers(user).namespace(namespace).build())


def alter(user, authentication_type, authorization_type, add_acl, delete_acl, operation_tuple, host, type,
          resource_type, resource_name, resource_pattern_type, quota_tuple, delete_quota_tuple, cluster, namespace):
    stream = get_resource_as_stream("kafkausers", resource_name=user, namespace=namespace)
    user_dict = yaml.full_load(stream)

    delete_last_applied_configuration(user_dict)

    if authentication_type is not None:
        if user_dict["spec"].get("authentication") is None:
            user_dict["spec"]["authentication"] = {}
        user_dict["spec"]["authentication"]["type"] = authentication_type

    if authorization_type is not None:
        if user_dict["spec"].get("authorization") is None:
            user_dict["spec"]["authorization"] = {}
        if authorization_type != "none":
            user_dict["spec"]["authorization"]["type"] = authorization_type
        else:
            user_dict["spec"].pop("authorization")

    if add_acl:
        if user_dict["spec"].get("authorization") is not None:
            _add_acl_option(user_dict, operation_tuple, host, type, resource_type, resource_name, resource_pattern_type)

    if delete_acl:
        if user_dict["spec"].get("authorization") is not None:
            _delete_acl_option(user_dict, operation_tuple, host, type, resource_type, resource_name,
                               resource_pattern_type)

    if len(quota_tuple) > 0:
        if user_dict["spec"].get("quotas") is None:
            user_dict["spec"]["quotas"] = {}
        add_kv_config_to_resource(quota_tuple, user_dict["spec"]["quotas"], snake_to_camel_case)

    if len(delete_quota_tuple) > 0:
        if user_dict["spec"].get("quotas") is not None:
            delete_resource_config(delete_quota_tuple, user_dict["spec"]["quotas"], snake_to_camel_case)

    user_yaml = yaml.dump(user_dict)
    user_temp_file = create_temp_file(user_yaml)

    os.system(
        Kubectl().apply().from_file("{user_temp_file_path}").namespace(namespace).build().format(
            user_temp_file_path=user_temp_file.name))

    user_temp_file.close()


def _add_acl_option(user_dict, operation, host, type, resource_type, resource_name, resource_pattern_type):
    if user_dict["spec"]["authorization"].get("acls") is None:
        user_dict["spec"]["authorization"]["acls"] = []
    for operation_str in operation:
        acl_dict = {"operation": operation_str, "host": host, "type": type,
                    "resource": {"type": resource_type, "name": resource_name, "patternType": resource_pattern_type}}
        user_dict["spec"]["authorization"]["acls"].append(acl_dict)


def _delete_acl_option(user_dict, operation, host, type, resource_type, resource_name, resource_pattern_type):
    if user_dict["spec"]["authorization"].get("acls") is None:
        user_dict["spec"]["authorization"]["acls"] = []
    for operation_str in operation:
        for acl_dict in user_dict["spec"]["authorization"]["acls"]:
            acl_dict_to_be_deleted = {'operation': operation_str, 'host': host, 'type': type,
                                      'resource': {'type': resource_type, 'name': resource_name,
                                                   'patternType': resource_pattern_type}}
            if acl_dict == acl_dict_to_be_deleted:
                user_dict["spec"]["authorization"]["acls"].remove(acl_dict)
