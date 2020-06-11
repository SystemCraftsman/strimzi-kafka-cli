import click
import os
import yaml

from kfk.command import kfk
from kfk.option_extensions import NotRequiredIf, RequiredIf
from kfk.commons import print_missing_options_for_command, download_strimzi_if_not_exists, resource_exists, \
    get_resource_as_file, delete_last_applied_configuration, add_resource_kv_config, delete_resource_config
from kfk.constants import *
from kfk.kubectl_command_builder import Kubectl


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--delete-quota', help='User quotas to be removed.', multiple=True)
@click.option('--quota', help='User\'s network and CPU utilization quotas in the Kafka cluster.', multiple=True)
@click.option('--alter', help='Alter authentication-type, quotas, etc. of the user.',
              is_flag=True)
@click.option('--delete', help='Delete a user.', is_flag=True)
@click.option('-o', '--output',
              help='Output format. One of: json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath'
                   '|jsonpath-file.')
@click.option('--describe', help='List details for the given user.', is_flag=True)
@click.option('--authentication-type', type=click.Choice(['tls', 'scram-sha-512'], case_sensitive=True), cls=RequiredIf,
              required_if='create')
@click.option('--create', help='Create a new user.', is_flag=True)
@click.option('--list', help='List all available users.', is_flag=True)
@click.option('--user', help='User Name', required=True, cls=NotRequiredIf, not_required_if='list')
@kfk.command()
def users(user, list, create, authentication_type, describe, output, delete, alter, quota, delete_quota, cluster,
          namespace):
    """The kafka user(s) to be created, altered or described."""
    if list:
        os.system(
            Kubectl().get().kafkausers().label("strimzi.io/cluster={cluster}").namespace(namespace).build().format(
                cluster=cluster))
    elif create:
        download_strimzi_if_not_exists()

        with open(r'{strimzi_path}/examples/user/kafka-user.yaml'.format(strimzi_path=STRIMZI_PATH).format(
                version=STRIMZI_VERSION)) as file:
            user_dict = yaml.full_load(file)

            user_dict["metadata"]["name"] = user
            user_dict["spec"]["authentication"]["type"] = authentication_type
            del user_dict["spec"]["authorization"]

            user_yaml = yaml.dump(user_dict)
            os.system(
                'echo "{user_yaml}" | '.format(user_yaml=user_yaml) + Kubectl().create().from_file("-").namespace(
                    namespace).build())

    elif describe:
        if output is not None:
            if resource_exists("kafkausers", user, cluster, namespace):
                os.system(Kubectl().get().kafkausers(user).namespace(namespace).output(output).build())
        else:
            if resource_exists("kafkausers", user, cluster, namespace):
                os.system(Kubectl().describe().kafkausers(user).namespace(namespace).build())
    elif delete:
        if resource_exists("kafkausers", user, cluster, namespace):
            os.system(Kubectl().delete().kafkausers(user).namespace(namespace).build())
    elif alter:
        if resource_exists("kafkausers", user, cluster, namespace):
            file = get_resource_as_file("kafkausers", user, namespace)
            user_dict = yaml.full_load(file)

            if authentication_type is not None:
                user_dict["spec"]["authentication"]["type"] = authentication_type

            delete_last_applied_configuration(user_dict)

            if len(quota) > 0:
                if user_dict["spec"].get("quotas") is None:
                    user_dict["spec"]["quotas"] = {}
                add_resource_kv_config(quota, user_dict["spec"]["quotas"])

            if len(delete_quota) > 0:
                if user_dict["spec"].get("quotas") is not None:
                    delete_resource_config(delete_quota, user_dict["spec"]["quotas"])

            topic_yaml = yaml.dump(user_dict)
            os.system(
                'echo "{topic_yaml}" | '.format(topic_yaml=topic_yaml) + Kubectl().apply().from_file("-").namespace(
                    namespace).build())
    else:
        print_missing_options_for_command("users")
