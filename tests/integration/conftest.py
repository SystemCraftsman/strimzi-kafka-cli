import subprocess
import time

import pytest
from click.testing import CliRunner

from kfk.main import kfk


def _cluster_is_reachable():
    try:
        result = subprocess.run(
            ["kubectl", "cluster-info"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


requires_cluster = pytest.mark.skipif(
    not _cluster_is_reachable(),
    reason="No Kubernetes cluster available",
)


@pytest.fixture(scope="session")
def namespace():
    return "kafka"


@pytest.fixture(scope="session")
def cluster():
    return "my-cluster"


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


@pytest.fixture(scope="session")
def kfk_cmd():
    return kfk


def wait_for_resource(resource_type, resource_name, namespace, timeout=300):
    """Wait for a Kubernetes resource to be ready."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                resource_type,
                resource_name,
                "-n",
                namespace,
                "-o",
                "jsonpath={.status.conditions[?(@.type=='Ready')].status}",
            ],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip() == "True":
            return True
        time.sleep(5)
    return False


def wait_for_deployment(name, namespace, timeout=300):
    """Wait for a deployment to be available."""
    result = subprocess.run(
        [
            "kubectl",
            "wait",
            f"deployment/{name}",
            "--for=condition=Available",
            f"--timeout={timeout}s",
            "-n",
            namespace,
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0
