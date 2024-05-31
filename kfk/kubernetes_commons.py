import base64
import json
import re
import sys
from os import path

import yaml
from kubernetes import client, config

config.load_kube_config()
api_client = client.ApiClient()


def yaml_object_argument_filter(func):
    def inner(k8s_api, yml_object, kind, **kwargs):
        if kind != "custom_object":
            kwargs.pop("version")
            kwargs.pop("group")
            kwargs.pop("plural")
        return func(k8s_api, yml_object, kind, **kwargs)

    return inner


def delete_object(name, resource_type, namespace):
    k8s_api = client.CoreV1Api(api_client)
    _delete_object(k8s_api, name, resource_type, namespace=namespace)
    print(f"{resource_type.capitalize()} `{name}` deleted.")


def create_registry_secret(
    name: str,
    registry: str,
    username: str,
    password: str,
):
    core_api = client.CoreV1Api(api_client)

    auth = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")

    docker_config_dict = {
        "auths": {
            registry: {
                "username": username,
                "password": password,
                "email": "",
                "auth": auth,
            }
        }
    }

    docker_config = base64.b64encode(
        json.dumps(docker_config_dict).encode("utf-8")
    ).decode("utf-8")

    core_api.create_namespaced_secret(
        namespace="default",
        body=client.V1Secret(
            metadata=client.V1ObjectMeta(
                name=name,
            ),
            type="kubernetes.io/dockerconfigjson",
            data={".dockerconfigjson": docker_config},
        ),
    )

    print(f"Registry Secret `{name}` created.")


def create_using_yaml(file_path, namespace):
    _operate_using_yaml(
        api_client,
        file_path,
        "create",
        yaml_objects=None,
        verbose=True,
        namespace=namespace,
    )


def delete_using_yaml(file_path, namespace):
    _operate_using_yaml(
        api_client,
        file_path,
        "delete",
        yaml_objects=None,
        verbose=True,
        namespace=namespace,
    )


def replace_using_yaml(file_path, namespace):
    _operate_using_yaml(
        api_client,
        file_path,
        "replace",
        yaml_objects=None,
        verbose=True,
        namespace=namespace,
    )


def _operate_using_yaml(
    k8s_client,
    yaml_file=None,
    operation=None,
    yaml_objects=None,
    verbose=False,
    namespace="default",
    **kwargs,
):
    def _operate_with(objects):
        failures = []
        k8s_objects = []
        for yml_object in objects:
            if yml_object is None:
                continue
            try:
                created = _operate_using_dict(
                    k8s_client,
                    yml_object,
                    operation,
                    verbose,
                    namespace=namespace,
                    **kwargs,
                )
                k8s_objects.append(created)
            except FailToExecuteError as failure:
                failures.extend(failure.api_exceptions)
        if failures:
            raise FailToExecuteError(failures)
        return k8s_objects

    if yaml_objects:
        yml_object_all = yaml_objects
        return _operate_with(yml_object_all)
    elif yaml_file:
        with open(path.abspath(yaml_file)) as f:
            yml_object_all = yaml.safe_load_all(f)
            return _operate_with(yml_object_all)
    else:
        raise ValueError(
            "One of `yaml_file` or `yaml_objects` arguments must be provided"
        )


def _operate_using_dict(
    k8s_client, yml_object, operation, verbose, namespace="default", **kwargs
):
    api_exceptions = []
    if "List" in yml_object["kind"]:
        kind = yml_object["kind"].replace("List", "")
        for yml_doc in yml_object["items"]:
            if kind != "":
                yml_doc["apiVersion"] = yml_object["apiVersion"]
                yml_doc["kind"] = kind
            try:
                _operate_using_dict_single_object(
                    k8s_client,
                    yml_doc,
                    operation,
                    verbose,
                    namespace=namespace,
                    **kwargs,
                )
            except client.rest.ApiException as api_exception:
                api_exceptions.append(api_exception)
    else:
        try:
            _operate_using_dict_single_object(
                k8s_client,
                yml_object,
                operation,
                verbose,
                namespace=namespace,
                **kwargs,
            )
        except client.rest.ApiException as api_exception:
            api_exceptions.append(api_exception)

    if api_exceptions:
        raise FailToExecuteError(api_exceptions)


def _operate_using_dict_single_object(
    k8s_client, yml_object, operation, verbose=False, namespace="default", **kwargs
):
    object_type = ""
    # get group and version from apiVersion
    group, _, version = yml_object["apiVersion"].partition("/")
    if version == "":
        version = group
        group = "core"
    # Take care for the case e.g. api_type is "apiextensions.k8s.io"
    group_prefix = "".join(group.rsplit(".k8s.io", 1))
    # convert group name from DNS subdomain format to
    # python class name convention
    group_prefix = "".join(word.capitalize() for word in group_prefix.split("."))
    func = "{0}{1}Api".format(group_prefix, version.capitalize())

    try:
        k8s_api = getattr(client, func)(k8s_client)
    except AttributeError:
        func = "CustomObjectsApi"
        k8s_api = getattr(client, func)(k8s_client)
        object_type = "custom_object"

    kind = yml_object["kind"]
    kind_snake_case = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", kind)
    object_type_from_kind = re.sub(
        "([a-z0-9])([A-Z])", r"\1_\2", kind_snake_case
    ).lower()
    name = yml_object["metadata"]["name"]

    if not object_type:
        object_type = object_type_from_kind

    getattr(sys.modules[__name__], f"_{operation}_using_yaml_object")(
        k8s_api,
        yml_object,
        object_type,
        version=version,
        group=group,
        plural=kind.lower() + "s",
        namespace=namespace,
    )
    if verbose:
        msg = f"{kind} `{name}` {operation}d."
        print(msg)


@yaml_object_argument_filter
def _create_using_yaml_object(k8s_api, yml_object, object_type, **kwargs):
    if hasattr(k8s_api, f"create_namespaced_{object_type}"):
        if "namespace" in yml_object["metadata"]:
            namespace = yml_object["metadata"]["namespace"]
            kwargs["namespace"] = namespace
        resp = getattr(k8s_api, f"create_namespaced_{object_type}")(
            body=yml_object, **kwargs
        )
    else:
        kwargs.pop("namespace", None)
        resp = getattr(k8s_api, f"create_{object_type}")(body=yml_object, **kwargs)
    return resp


@yaml_object_argument_filter
def _delete_using_yaml_object(k8s_api, yml_object, object_type, **kwargs):
    if "namespace" in yml_object["metadata"]:
        namespace = yml_object["metadata"]["namespace"]
        kwargs["namespace"] = namespace
    name = yml_object["metadata"]["name"]
    _delete_object(k8s_api, name, object_type, **kwargs)


@yaml_object_argument_filter
def _replace_using_yaml_object(k8s_api, yml_object, object_type, **kwargs):
    if hasattr(k8s_api, f"replace_namespaced_{object_type}"):
        if "namespace" in yml_object["metadata"]:
            namespace = yml_object["metadata"]["namespace"]
            kwargs["namespace"] = namespace
        resp = getattr(k8s_api, f"replace_namespaced_{object_type}")(
            body=yml_object, **kwargs
        )
    else:
        kwargs.pop("namespace", None)
        resp = getattr(k8s_api, f"replace_{object_type}")(body=yml_object, **kwargs)
    return resp


def _delete_object(k8s_api, name, object_type, delete_options_version="V1", **kwargs):
    try:
        if hasattr(k8s_api, f"delete_namespaced_{object_type}"):
            resp = getattr(k8s_api, f"delete_namespaced_{object_type}")(
                name=name,
                body=getattr(client, f"{delete_options_version}DeleteOptions")(
                    propagation_policy="Background", grace_period_seconds=5
                ),
                **kwargs,
            )
        else:
            kwargs.pop("namespace", None)
            resp = getattr(k8s_api, f"delete_{object_type}")(
                name=name,
                body=getattr(client, f"{delete_options_version}DeleteOptions")(
                    propagation_policy="Background", grace_period_seconds=5
                ),
                **kwargs,
            )
        return resp
    except client.rest.ApiException as api_exception:
        if api_exception.reason != "Not Found":
            raise api_exception


class FailToExecuteError(Exception):
    """An exception class for handling error if an error occurred when handling
    a yaml file during creation or deletion of the resource."""

    def __init__(self, api_exceptions):
        self.api_exceptions = api_exceptions

    def __str__(self):
        msg = ""
        for api_exception in self.api_exceptions:
            msg += "Error from server ({0}):{1}".format(
                api_exception.reason, api_exception.body
            )
        return msg
