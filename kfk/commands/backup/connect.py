import click

from kfk.commands.backup import backup
from kfk.commands.backup.commons import (
    clean_metadata,
    create_archive,
    extract_archive,
    get_custom_resources,
    restore_custom_resource,
)


@backup.command()
@click.option("--cluster", required=True, help="Kafka Connect cluster name")
@click.option("-n", "--namespace", required=True, help="Namespace")
@click.option("-o", "--output", default=None, help="Output archive path")
@click.option("--restore", "do_restore", is_flag=True, help="Restore from backup")
@click.option(
    "--from", "from_backup", default=None, help="Backup archive to restore from"
)
def connect(cluster, namespace, output, do_restore, from_backup):
    """Backs up or restores a Kafka Connect cluster and its connectors."""
    if do_restore:
        _restore(from_backup, namespace, cluster)
    else:
        _backup(cluster, namespace, output)


def _backup(cluster, namespace, output):
    if not output:
        output = f"{cluster}-connect-backup.tar.gz"

    click.echo(
        f"Backing up Kafka Connect cluster '{cluster}' in namespace '{namespace}'..."
    )
    resources = {}

    connects = get_custom_resources("kafkaconnects", namespace)
    for kc in connects:
        if kc["metadata"]["name"] == cluster:
            resources["connect.yaml"] = clean_metadata(kc)
            click.echo(f"  KafkaConnect/{cluster}")
            break
    else:
        click.echo(
            f"KafkaConnect cluster '{cluster}' not found in namespace '{namespace}'"
        )
        raise SystemExit(1)

    connectors = get_custom_resources(
        "kafkaconnectors", namespace, label=f"strimzi.io/cluster={cluster}"
    )
    for connector in connectors:
        name = connector["metadata"]["name"]
        resources[f"connectors/{name}.yaml"] = clean_metadata(connector)
        click.echo(f"  KafkaConnector/{name}")

    create_archive(resources, output)
    click.echo(f"Backup saved to {output} ({len(resources)} resources)")


def _restore(from_backup, namespace, cluster):
    if not from_backup:
        click.echo("--from is required for restore")
        raise SystemExit(1)

    click.echo(f"Restoring from '{from_backup}' to namespace '{namespace}'...")
    resources = extract_archive(from_backup)

    if "connect.yaml" in resources:
        resource = resources["connect.yaml"]
        resource["metadata"]["name"] = cluster
        restore_custom_resource(resource, namespace)

    for name, resource in sorted(resources.items()):
        if name.startswith("connectors/"):
            restore_custom_resource(resource, namespace)

    click.echo(f"Restore complete ({len(resources)} resources)")
