import json

import click
import yaml

from kfk.commands.main import kfk
from kfk.commons import (
    add_kv_config_to_resource,
    create_temp_file,
    delete_last_applied_configuration,
    delete_resource_config,
    get_resource_as_stream,
    open_file_in_system_editor,
    raise_exception_for_missing_options,
)
from kfk.config import STRIMZI_PATH, STRIMZI_VERSION
from kfk.kubernetes_commons import (
    create_using_yaml,
    delete_using_yaml,
    describe_resource,
    edit_resource,
    get_resource,
    list_resource,
    replace_using_yaml,
)
from kfk.messages import Messages
from kfk.option_extensions import NotRequiredIf, RequiredIf, RequiredIfValue
from kfk.utils import parse_kv_string


@click.option("-y", "--yes", "is_yes", help='"Yes" confirmation', is_flag=True)
@click.option(
    "-n",
    "--namespace",
    help="Namespace to use",
    required=True,
    cls=NotRequiredIf,
    options=["is_list"],
)
@click.option(
    "--delete-listener",
    help="A listener to be removed from the cluster (by name).",
    multiple=True,
)
@click.option(
    "--authorizer-class",
    help="Fully qualified authorizer class name for custom authorization.",
    cls=RequiredIfValue,
    option_value_pairs={"authorization_type": "custom"},
)
@click.option(
    "--super-user",
    help="A super user for cluster authorization.",
    multiple=True,
)
@click.option(
    "--authorization-type",
    help="Authorization type for the cluster.",
    type=click.Choice(["simple", "custom", "none"], case_sensitive=True),
    cls=RequiredIf,
    options=["super_user"],
)
@click.option(
    "--listener-auth",
    help=(
        "Authentication config for the listener being added."
        " Format: type=T,validIssuerUri=U,clientId=C"
    ),
)
@click.option(
    "--add-listener",
    help=(
        "A listener to be added to the cluster."
        " Format: name=X,port=N,type=T,tls=BOOL"
    ),
    multiple=True,
    cls=RequiredIf,
    options=["listener_auth"],
)
@click.option(
    "--delete-config",
    help="A cluster configuration override to be removed for an existing cluster",
    multiple=True,
)
@click.option(
    "--config",
    help="A cluster configuration override for the cluster being altered.",
    multiple=True,
)
@click.option("--alter", "is_alter", help="Alters the Kafka cluster.", is_flag=True)
@click.option("--delete", "is_delete", help="Deletes the Kafka cluster.", is_flag=True)
@click.option(
    "--replicas", help="The number of broker replicas for the cluster.", type=int
)
@click.option("--create", "is_create", help="Creates a Kafka cluster.", is_flag=True)
@click.option(
    "--describe",
    "is_describe",
    help="Lists details for the given cluster.",
    is_flag=True,
)
@click.option(
    "-o",
    "--output",
    help=(
        "Output format. One of:"
        " json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath"
        "|jsonpath-file."
    ),
)
@click.option(
    "--list",
    "is_list",
    help="List all available clusters.",
    required=True,
    is_flag=True,
)
@click.option(
    "--cluster",
    help="Cluster Name",
    required=True,
    cls=NotRequiredIf,
    options=["is_list"],
)
@kfk.command()
def clusters(
    cluster,
    is_list,
    is_create,
    replicas,
    is_describe,
    is_delete,
    is_alter,
    config,
    delete_config,
    add_listener,
    listener_auth,
    delete_listener,
    authorization_type,
    super_user,
    authorizer_class,
    output,
    namespace,
    is_yes,
):
    """Creates, alters, deletes, describes Kafka cluster(s)."""
    if is_list:
        list(namespace)
    elif is_create:
        create(
            cluster, replicas, config, add_listener, listener_auth, namespace, is_yes
        )
    elif is_describe:
        describe(cluster, output, namespace)
    elif is_delete:
        delete(cluster, namespace, is_yes)
    elif is_alter:
        alter(
            cluster,
            replicas,
            config,
            delete_config,
            add_listener,
            listener_auth,
            delete_listener,
            authorization_type,
            super_user,
            authorizer_class,
            namespace,
        )
    else:
        raise_exception_for_missing_options("clusters")


def list(namespace):
    list_resource("kafkas", namespace)


def create(cluster, replicas, config, add_listener, listener_auth, namespace, is_yes):
    with open(
        "{strimzi_path}/examples/kafka/kafka-ephemeral.yaml".format(
            strimzi_path=STRIMZI_PATH
        ).format(version=STRIMZI_VERSION)
    ) as file:
        stream = file.read()

        docs = [doc for doc in yaml.full_load_all(stream)]

        kafka_dict, broker_dict = _get_kafka_and_broker_dicts(docs)

        kafka_dict["metadata"]["name"] = cluster

        for doc in docs:
            if doc["kind"] == "KafkaNodePool":
                doc["metadata"]["labels"]["strimzi.io/cluster"] = cluster

        _update_replicas(replicas, kafka_dict, broker_dict)

        _add_config_if_provided(config, kafka_dict)

        _add_listeners_if_provided(add_listener, kafka_dict, listener_auth)

        cluster_yaml = yaml.dump_all(docs)
        cluster_temp_file = create_temp_file(cluster_yaml)

        if is_yes:
            is_confirmed = True
        else:
            open_file_in_system_editor(cluster_temp_file.name)
            is_confirmed = click.confirm(Messages.CLUSTER_CREATE_CONFIRMATION)
        if is_confirmed:
            create_using_yaml(cluster_temp_file.name, namespace)

        cluster_temp_file.close()


def describe(cluster, output, namespace):
    if output is not None:
        resource = get_resource("kafkas", cluster, namespace)
        if output == "yaml":
            click.echo(yaml.dump(resource, default_flow_style=False))
        elif output == "json":
            click.echo(json.dumps(resource, indent=2))
    else:
        describe_resource("kafkas", cluster, namespace)


def delete(cluster, namespace, is_yes):
    if is_yes:
        is_confirmed = True
    else:
        is_confirmed = click.confirm(Messages.CLUSTER_DELETE_CONFIRMATION)
    if is_confirmed:
        with open(
            "{strimzi_path}/examples/kafka/kafka-ephemeral.yaml".format(
                strimzi_path=STRIMZI_PATH
            ).format(version=STRIMZI_VERSION)
        ) as file:
            stream = file.read()

            docs = [doc for doc in yaml.full_load_all(stream)]

            kafka_dict, _ = _get_kafka_and_broker_dicts(docs)

            kafka_dict["metadata"]["name"] = cluster

            for doc in docs:
                if doc["kind"] == "KafkaNodePool":
                    doc["metadata"]["labels"]["strimzi.io/cluster"] = cluster

            cluster_yaml = yaml.dump_all(docs)
            cluster_temp_file = create_temp_file(cluster_yaml)

            delete_using_yaml(cluster_temp_file.name, namespace)

            cluster_temp_file.close()


def alter(
    cluster,
    replicas,
    config,
    delete_config,
    add_listener,
    listener_auth,
    delete_listener,
    authorization_type,
    super_user,
    authorizer_class,
    namespace,
):
    has_changes = (
        len(config) > 0
        or len(delete_config) > 0
        or len(add_listener) > 0
        or len(delete_listener) > 0
        or replicas is not None
        or authorization_type is not None
    )
    if has_changes:
        stream = get_resource_as_stream(
            "kafkas", resource_name=cluster, namespace=namespace
        )
        cluster_dict = yaml.full_load(stream)

        delete_last_applied_configuration(cluster_dict)

        _update_replicas(replicas, cluster_dict)

        _add_config_if_provided(config, cluster_dict)

        if len(delete_config) > 0:
            if cluster_dict["spec"]["kafka"].get("config") is not None:
                delete_resource_config(
                    delete_config, cluster_dict["spec"]["kafka"]["config"]
                )

        _add_listeners_if_provided(add_listener, cluster_dict, listener_auth)
        _delete_listeners_if_provided(delete_listener, cluster_dict)
        _set_authorization_if_provided(
            authorization_type, super_user, authorizer_class, cluster_dict
        )

        cluster_yaml = yaml.dump(cluster_dict)
        cluster_temp_file = create_temp_file(cluster_yaml)

        replace_using_yaml(cluster_temp_file.name, namespace)

        cluster_temp_file.close()

        if replicas is not None:
            _update_broker_replicas(replicas, namespace)
    else:
        edit_resource("kafkas", cluster, namespace)


def _get_kafka_and_broker_dicts(docs):
    kafka_dict = None
    broker_dict = None
    for doc in docs:
        if doc["kind"] == "Kafka":
            kafka_dict = doc
        elif doc["kind"] == "KafkaNodePool" and "broker" in doc["spec"].get(
            "roles", []
        ):
            broker_dict = doc
    return kafka_dict, broker_dict


def _update_replicas(replicas, kafka_dict, broker_dict=None):
    if replicas is not None:
        min_insync_replicas = 1
        if replicas > 1:
            min_insync_replicas = replicas - 1
        kafka_dict["spec"]["kafka"]["config"]["offsets.topic.replication.factor"] = int(
            replicas
        )
        kafka_dict["spec"]["kafka"]["config"][
            "transaction.state.log.replication.factor"
        ] = int(replicas)
        kafka_dict["spec"]["kafka"]["config"]["default.replication.factor"] = int(
            replicas
        )
        kafka_dict["spec"]["kafka"]["config"][
            "transaction.state.log.min.isr"
        ] = min_insync_replicas
        kafka_dict["spec"]["kafka"]["config"][
            "min.insync.replicas"
        ] = min_insync_replicas

        if broker_dict is not None:
            broker_dict["spec"]["replicas"] = int(replicas)


def _update_broker_replicas(replicas, namespace):
    stream = get_resource_as_stream(
        "kafkanodepools", resource_name="broker", namespace=namespace
    )
    broker_dict = yaml.full_load(stream)

    delete_last_applied_configuration(broker_dict)

    broker_dict["spec"]["replicas"] = int(replicas)

    broker_yaml = yaml.dump(broker_dict)
    broker_temp_file = create_temp_file(broker_yaml)

    replace_using_yaml(broker_temp_file.name, namespace)

    broker_temp_file.close()


def _add_config_if_provided(config, cluster_dict):
    if len(config) > 0:
        if cluster_dict["spec"]["kafka"].get("config") is None:
            cluster_dict["spec"]["kafka"]["config"] = {}
        add_kv_config_to_resource(config, cluster_dict["spec"]["kafka"]["config"])


def _add_listeners_if_provided(add_listener, cluster_dict, listener_auth=None):
    if len(add_listener) > 0:
        listeners = cluster_dict["spec"]["kafka"].setdefault("listeners", [])
        for listener_str in add_listener:
            new_listener = parse_kv_string(listener_str)
            if listener_auth:
                new_listener["authentication"] = parse_kv_string(listener_auth)
            for existing in listeners:
                if existing["name"] == new_listener["name"]:
                    existing.update(new_listener)
                    break
            else:
                listeners.append(new_listener)


def _delete_listeners_if_provided(delete_listener, cluster_dict):
    if len(delete_listener) > 0:
        listeners = cluster_dict["spec"]["kafka"].get("listeners", [])
        cluster_dict["spec"]["kafka"]["listeners"] = [
            listener
            for listener in listeners
            if listener["name"] not in delete_listener
        ]


def _set_authorization_if_provided(
    authorization_type, super_user, authorizer_class, cluster_dict
):
    if authorization_type is not None:
        if authorization_type == "none":
            cluster_dict["spec"]["kafka"].pop("authorization", None)
        else:
            auth = {"type": authorization_type}
            if len(super_user) > 0:
                auth["superUsers"] = [*super_user]
            if authorizer_class is not None:
                auth["authorizerClass"] = authorizer_class
            cluster_dict["spec"]["kafka"]["authorization"] = auth
