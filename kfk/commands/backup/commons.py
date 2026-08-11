import tarfile
from io import BytesIO

import click
import yaml
from kubernetes import client

from kfk.kubernetes_commons import (
    STRIMZI_API_VERSION,
    STRIMZI_GROUP,
    api_client,
    custom_objects_api,
)

METADATA_FIELDS_TO_STRIP = [
    "creationTimestamp",
    "generation",
    "managedFields",
    "resourceVersion",
    "selfLink",
    "uid",
]

ANNOTATION_KEYS_TO_STRIP = [
    "kubectl.kubernetes.io/last-applied-configuration",
]


def clean_metadata(resource):
    metadata = resource.get("metadata", {})
    for field in METADATA_FIELDS_TO_STRIP:
        metadata.pop(field, None)
    metadata.pop("ownerReferences", None)
    annotations = metadata.get("annotations", {})
    for key in ANNOTATION_KEYS_TO_STRIP:
        annotations.pop(key, None)
    if not annotations:
        metadata.pop("annotations", None)
    resource.pop("status", None)
    return resource


def get_custom_resources(resource_type, namespace, label=None):
    kwargs = {
        "group": STRIMZI_GROUP,
        "version": STRIMZI_API_VERSION,
        "namespace": namespace,
        "plural": resource_type,
    }
    if label:
        kwargs["label_selector"] = label
    result = custom_objects_api.list_namespaced_custom_object(**kwargs)
    return result.get("items", [])


def get_secrets(namespace, label_selector):
    core_api = client.CoreV1Api(api_client)
    result = core_api.list_namespaced_secret(
        namespace=namespace, label_selector=label_selector
    )
    return [s.to_dict() for s in result.items]


def clean_secret_metadata(secret):
    metadata = secret.get("metadata", {})
    for field in METADATA_FIELDS_TO_STRIP:
        metadata.pop(field, None)
    metadata.pop("owner_references", None)
    annotations = metadata.get("annotations", {})
    for key in ANNOTATION_KEYS_TO_STRIP:
        annotations.pop(key, None)
    if not annotations:
        metadata.pop("annotations", None)
    return secret


def create_archive(resources_dict, output_path):
    with tarfile.open(output_path, "w:gz") as tar:
        for filename, content in resources_dict.items():
            data = yaml.dump(content, default_flow_style=False).encode("utf-8")
            info = tarfile.TarInfo(name=filename)
            info.size = len(data)
            tar.addfile(info, BytesIO(data))


def extract_archive(archive_path):
    resources = {}
    with tarfile.open(archive_path, "r:gz") as tar:
        for member in tar.getmembers():
            f = tar.extractfile(member)
            if f:
                resources[member.name] = yaml.safe_load(f.read())
    return resources


def restore_custom_resource(resource, namespace):
    resource["metadata"]["namespace"] = namespace
    kind = resource.get("kind", "")
    plural = kind.lower() + "s"
    try:
        custom_objects_api.create_namespaced_custom_object(
            group=STRIMZI_GROUP,
            version=STRIMZI_API_VERSION,
            namespace=namespace,
            plural=plural,
            body=resource,
        )
        click.echo(f"  Restored {kind}/{resource['metadata']['name']}")
    except client.exceptions.ApiException as e:
        if e.status == 409:
            click.echo(
                f"  {kind}/{resource['metadata']['name']} already exists, skipping"
            )
        else:
            raise


def restore_secret(secret, namespace):
    core_api = client.CoreV1Api(api_client)
    secret["metadata"]["namespace"] = namespace
    name = secret["metadata"]["name"]
    body = client.V1Secret(
        api_version="v1",
        kind="Secret",
        metadata=client.V1ObjectMeta(
            name=name,
            namespace=namespace,
            labels=secret["metadata"].get("labels"),
            annotations=secret["metadata"].get("annotations"),
        ),
        data=secret.get("data"),
        type=secret.get("type", "Opaque"),
    )
    try:
        core_api.create_namespaced_secret(namespace=namespace, body=body)
        click.echo(f"  Restored Secret/{name}")
    except client.exceptions.ApiException as e:
        if e.status == 409:
            click.echo(f"  Secret/{name} already exists, skipping")
        else:
            raise
