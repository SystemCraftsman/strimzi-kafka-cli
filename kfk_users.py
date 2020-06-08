import click
import os
import yaml

from kfk import kfk
from option_extensions import NotRequiredIf, RequiredIf
from commons import print_missing_options_for_command, download_strimzi_if_not_exists
from constants import *
from kubectl_command_builder import Kubectl


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
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
def users(user, list, create, authentication_type, describe, output, delete, cluster, namespace):
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
            if user_exists(user, cluster, namespace):
                os.system(Kubectl().get().kafkausers(user).namespace(namespace).output(output).build())
        else:
            if user_exists(user, cluster, namespace):
                os.system(Kubectl().describe().kafkausers(user).namespace(namespace).build())
    elif delete:
        if user_exists(user, cluster, namespace):
            os.system(Kubectl().delete().kafkausers(user).namespace(namespace).build())
    else:
        print_missing_options_for_command("users")


def user_exists(user, cluster, namespace):
    return user in os.popen(
        Kubectl().get().kafkausers().label("strimzi.io/cluster={cluster}").namespace(namespace).build().format(
            cluster=cluster)).read()
