import platform
import sys

from pathlib import Path

BASE_FOLDER = ".strimzi-kafka-cli"
BASE_PATH = str(Path.home()) + "/" + BASE_FOLDER
STRIMZI_VERSION = "0.18.0"
STRIMZI_PATH = BASE_PATH + "/strimzi-{version}".format(version=STRIMZI_VERSION)
STRIMZI_RELEASE_URL = "https://github.com/strimzi/strimzi-kafka-operator/releases/download/{version}/strimzi-{version}.tar.gz".format(
    version=STRIMZI_VERSION)
KUBECTL_VERSION = "v1.18.0"
KUBECTL = "kubectl" if platform.system().lower() != "windows" else "kubectl.exe"
KUBECTL_PATH = BASE_PATH + "/" + KUBECTL
PROCESSOR_TYPE = "amd64" if sys.maxsize > 2 ** 32 else "386"
KUBECTL_RELEASE_URL = "https://storage.googleapis.com/kubernetes-release/release/{version}/bin/{operating_system}/{processor_type}/{kubectl}".format(
    version=KUBECTL_VERSION, operating_system=platform.system().lower(), processor_type=PROCESSOR_TYPE, kubectl=KUBECTL)
SPACE = " "
