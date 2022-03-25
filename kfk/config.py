import platform
import sys
import os

from pathlib import Path

STRIMZI_VERSION = "0.26.1"
KUBECTL_VERSION = "v1.23.5"


def _get_processor_type():
    if _is_64_bit():
        if "arm" in platform.uname().machine or "aarch" in platform.uname().machine:
            return "arm64"
        else:
            return "amd64"
    else:
        if "arm" in platform.uname().machine:
            return "arm"
        else:
            return "386"


def _is_64_bit():
    return sys.maxsize > 2 ** 32


BASE_FOLDER = ".strimzi-kafka-cli"
BASE_PATH = (str(Path.home()) + "/" + BASE_FOLDER) if os.environ.get(
    'STRIMZI_KAFKA_CLI_BASE_PATH') is None else os.environ.get('STRIMZI_KAFKA_CLI_BASE_PATH')
STRIMZI_VERSION = STRIMZI_VERSION if os.environ.get('STRIMZI_KAFKA_CLI_STRIMZI_VERSION') is None else os.environ.get(
    'STRIMZI_KAFKA_CLI_STRIMZI_VERSION')
STRIMZI_PATH = (BASE_PATH + f"/strimzi-{STRIMZI_VERSION}") if os.environ.get(
    'STRIMZI_KAFKA_CLI_STRIMZI_PATH') is None else os.environ.get('STRIMZI_KAFKA_CLI_STRIMZI_PATH')
STRIMZI_RELEASE_URL = f"https://github.com/strimzi/strimzi-kafka-operator/releases/download/{STRIMZI_VERSION}/strimzi-{STRIMZI_VERSION}.tar.gz"
KUBECTL_VERSION = KUBECTL_VERSION if os.environ.get('STRIMZI_KAFKA_CLI_KUBECTL_VERSION') is None else os.environ.get(
    'STRIMZI_KAFKA_CLI_KUBECTL_VERSION')
KUBECTL = "kubectl" if platform.system().lower() != "windows" else "kubectl.exe"
KUBECTL_PATH = (BASE_PATH + "/" + KUBECTL) if os.environ.get(
    'STRIMZI_KAFKA_CLI_KUBECTL_PATH') is None else os.environ.get('STRIMZI_KAFKA_CLI_KUBECTL_PATH')
PROCESSOR_TYPE = _get_processor_type()
KUBECTL_RELEASE_URL = f"https://storage.googleapis.com/kubernetes-release/release/{KUBECTL_VERSION}/bin/{platform.system().lower()}/{PROCESSOR_TYPE}/{KUBECTL}"
