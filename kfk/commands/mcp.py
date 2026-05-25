import click

from kfk.commands.main import kfk


@kfk.command()
def mcp():
    """Start the Strimzi MCP server."""
    try:
        from kfk.mcp_server import mcp as mcp_server
    except ImportError:
        raise click.ClickException(
            "MCP dependencies not installed." " Run: pip install strimzi-kafka-cli[mcp]"
        )
    mcp_server.run()
