import click

from kfk.commands.backup import backup
from kfk.commands.backup.commons import (
    clean_metadata,
    clean_secret_metadata,
    create_archive,
    extract_archive,
    get_custom_resources,
    get_secrets,
    restore_custom_resource,
    restore_secret,
)


@backup.command()
@click.option("--cluster", required=True, help="Kafka cluster name")
@click.option("-n", "--namespace", required=True, help="Namespace")
@click.option("-o", "--output", default=None, help="Output archive path")
@click.option("--restore", "do_restore", is_flag=True, help="Restore from backup")
@click.option(
    "--from", "from_backup", default=None, help="Backup archive to restore from"
)
@click.option(
    "--include-secrets", is_flag=True, default=False, help="Include CA and user secrets"
)
def kafka(cluster, namespace, output, do_restore, from_backup, include_secrets):
    """Backs up or restores a Kafka cluster and its resources."""
    if do_restore:
        _restore(from_backup, namespace, cluster)
    else:
        _backup(cluster, namespace, output, include_secrets)


def _backup(cluster, namespace, output, include_secrets):
    if not output:
        output = f"{cluster}-backup.tar.gz"

    click.echo(f"Backing up Kafka cluster '{cluster}' in namespace '{namespace}'...")
    resources = {}

    kafkas = get_custom_resources("kafkas", namespace)
    for k in kafkas:
        if k["metadata"]["name"] == cluster:
            resources["kafka.yaml"] = clean_metadata(k)
            click.echo(f"  Kafka/{cluster}")
            break
    else:
        click.echo(f"Kafka cluster '{cluster}' not found in namespace '{namespace}'")
        raise SystemExit(1)

    node_pools = get_custom_resources(
        "kafkanodepools", namespace, label=f"strimzi.io/cluster={cluster}"
    )
    for i, np in enumerate(node_pools):
        name = np["metadata"]["name"]
        resources[f"nodepools/{name}.yaml"] = clean_metadata(np)
        click.echo(f"  KafkaNodePool/{name}")

    topics = get_custom_resources(
        "kafkatopics", namespace, label=f"strimzi.io/cluster={cluster}"
    )
    for topic in topics:
        name = topic["metadata"]["name"]
        resources[f"topics/{name}.yaml"] = clean_metadata(topic)
        click.echo(f"  KafkaTopic/{name}")

    users = get_custom_resources(
        "kafkausers", namespace, label=f"strimzi.io/cluster={cluster}"
    )
    for user in users:
        name = user["metadata"]["name"]
        resources[f"users/{name}.yaml"] = clean_metadata(user)
        click.echo(f"  KafkaUser/{name}")

    if include_secrets:
        ca_secrets = get_secrets(
            namespace, f"strimzi.io/cluster={cluster},strimzi.io/kind=Kafka"
        )
        for secret in ca_secrets:
            name = secret["metadata"]["name"]
            resources[f"secrets/{name}.yaml"] = clean_secret_metadata(secret)
            click.echo(f"  Secret/{name}")

        for user in users:
            user_name = user["metadata"]["name"]
            label = (
                f"strimzi.io/cluster={cluster},"
                f"strimzi.io/kind=KafkaUser,"
                f"strimzi.io/name={user_name}"
            )
            user_secrets = get_secrets(namespace, label)
            for secret in user_secrets:
                name = secret["metadata"]["name"]
                resources[f"secrets/{name}.yaml"] = clean_secret_metadata(secret)
                click.echo(f"  Secret/{name}")

    create_archive(resources, output)
    click.echo(f"Backup saved to {output} ({len(resources)} resources)")


def _restore(from_backup, namespace, cluster):
    if not from_backup:
        click.echo("--from is required for restore")
        raise SystemExit(1)

    click.echo(f"Restoring from '{from_backup}' to namespace '{namespace}'...")
    resources = extract_archive(from_backup)

    if "kafka.yaml" in resources:
        resource = resources["kafka.yaml"]
        resource["metadata"]["name"] = cluster
        restore_custom_resource(resource, namespace)

    for name, resource in sorted(resources.items()):
        if name.startswith("nodepools/"):
            restore_custom_resource(resource, namespace)

    for name, resource in sorted(resources.items()):
        if name.startswith("topics/"):
            restore_custom_resource(resource, namespace)

    for name, resource in sorted(resources.items()):
        if name.startswith("users/"):
            restore_custom_resource(resource, namespace)

    for name, resource in sorted(resources.items()):
        if name.startswith("secrets/"):
            restore_secret(resource, namespace)

    click.echo(f"Restore complete ({len(resources)} resources)")
