import re
import sys
from os import path

import yaml
from kubernetes import client, config

config.load_kube_config()
k8s_client = client.ApiClient()


def delete_object(name, kind, namespace):
    k8s_api = client.CoreV1Api(k8s_client)
    _delete_object(k8s_api, name, kind, namespace=namespace)


def create_using_yaml(file_path, namespace):
    _operate_using_yaml(
        k8s_client,
        file_path,
        "create",
        yaml_objects=None,
        verbose=True,
        namespace=namespace,
    )


def delete_using_yaml(file_path, namespace):
    _operate_using_yaml(
        k8s_client,
        file_path,
        "delete",
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
    def operate_with(objects):
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
        return operate_with(yml_object_all)
    elif yaml_file:
        with open(path.abspath(yaml_file)) as f:
            yml_object_all = yaml.safe_load_all(f)
            return operate_with(yml_object_all)
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
    # get group and version from apiVersion
    group, _, version = yml_object["apiVersion"].partition("/")
    if version == "":
        version = group
        group = "core"
    # Take care for the case e.g. api_type is "apiextensions.k8s.io"
    group = "".join(group.rsplit(".k8s.io", 1))
    # convert group name from DNS subdomain format to
    # python class name convention
    group = "".join(word.capitalize() for word in group.split("."))
    func = "{0}{1}Api".format(group, version.capitalize())
    k8s_api = getattr(client, func)(k8s_client)
    kind = yml_object["kind"]
    kind = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", kind)
    kind = re.sub("([a-z0-9])([A-Z])", r"\1_\2", kind).lower()
    name = yml_object["metadata"]["name"]

    getattr(sys.modules[__name__], f"_{operation}_using_yaml_object")(
        k8s_api, yml_object, kind, version.capitalize(), namespace=namespace
    )
    if verbose:
        msg = f"{kind} `{name}` {operation}d."
        print(msg)


def _create_using_yaml_object(k8s_api, yml_object, kind, version, **kwargs):
    if hasattr(k8s_api, f"create_namespaced_{kind}"):
        if "namespace" in yml_object["metadata"]:
            namespace = yml_object["metadata"]["namespace"]
            kwargs["namespace"] = namespace
        resp = getattr(k8s_api, "create_namespaced_{0}".format(kind))(
            body=yml_object, **kwargs
        )
    else:
        kwargs.pop("namespace", None)
        resp = getattr(k8s_api, "create_{0}".format(kind))(body=yml_object, **kwargs)
    return resp


def _delete_using_yaml_object(k8s_api, yml_object, kind, version, **kwargs):
    if "namespace" in yml_object["metadata"]:
        namespace = yml_object["metadata"]["namespace"]
        kwargs["namespace"] = namespace
    name = yml_object["metadata"]["name"]
    delete_object(k8s_api, name, kind, version, **kwargs)


def _delete_object(k8s_api, name, kind, version="V1", **kwargs):
    try:
        if hasattr(k8s_api, "delete_namespaced_{0}".format(kind)):
            resp = getattr(k8s_api, "delete_namespaced_{}".format(kind))(
                name=name,
                body=getattr(client, f"{version}DeleteOptions")(
                    propagation_policy="Background", grace_period_seconds=5
                ),
                **kwargs,
            )
        else:
            kwargs.pop("namespace", None)
            resp = getattr(k8s_api, "delete_{}".format(kind))(
                name=name,
                body=getattr(client, f"{version}DeleteOptions")(
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
