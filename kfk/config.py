import platform
import sys
import os

from pathlib import Path

STRIMZI_VERSION = "0.20.0"
KUBECTL_VERSION = "v1.19.0"

BASE_FOLDER = ".strimzi-kafka-cli"
BASE_PATH = (str(Path.home()) + "/" + BASE_FOLDER) if os.environ.get(
    'STRIMZI_KAFKA_CLI_BASE_PATH') is None else os.environ.get('STRIMZI_KAFKA_CLI_BASE_PATH')
STRIMZI_VERSION = STRIMZI_VERSION if os.environ.get('STRIMZI_KAFKA_CLI_STRIMZI_VERSION') is None else os.environ.get('STRIMZI_KAFKA_CLI_STRIMZI_VERSION')
STRIMZI_PATH = (BASE_PATH + "/strimzi-{version}".format(version=STRIMZI_VERSION)) if os.environ.get(
    'STRIMZI_KAFKA_CLI_STRIMZI_PATH') is None else os.environ.get('STRIMZI_KAFKA_CLI_STRIMZI_PATH')
STRIMZI_RELEASE_URL = "https://github.com/strimzi/strimzi-kafka-operator/releases/download/{version}/strimzi-{version}.tar.gz".format(
    version=STRIMZI_VERSION)
KUBECTL_VERSION = KUBECTL_VERSION if os.environ.get('STRIMZI_KAFKA_CLI_KUBECTL_VERSION') is None else os.environ.get('STRIMZI_KAFKA_CLI_KUBECTL_VERSION')
KUBECTL = "kubectl" if platform.system().lower() != "windows" else "kubectl.exe"
KUBECTL_PATH = (BASE_PATH + "/" + KUBECTL) if os.environ.get(
    'STRIMZI_KAFKA_CLI_KUBECTL_PATH') is None else os.environ.get('STRIMZI_KAFKA_CLI_KUBECTL_PATH')
PROCESSOR_TYPE = "amd64" if sys.maxsize > 2 ** 32 else "386"
KUBECTL_RELEASE_URL = "https://storage.googleapis.com/kubernetes-release/release/{version}/bin/{operating_system}/{processor_type}/{kubectl}".format(
    version=KUBECTL_VERSION, operating_system=platform.system().lower(), processor_type=PROCESSOR_TYPE, kubectl=KUBECTL)
