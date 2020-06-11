import platform

from pathlib import Path

BASE_FOLDER = ".strimzi-kafka-cli"
BASE_PATH = str(Path.home()) + "/" + BASE_FOLDER
STRIMZI_VERSION = "0.18.0"
STRIMZI_PATH = BASE_PATH + "/strimzi-{version}".format(version=STRIMZI_VERSION)
STRIMZI_RELEASE_URL = "https://github.com/strimzi/strimzi-kafka-operator/releases/download/{version}/strimzi-{version}.tar.gz".format(
    version=STRIMZI_VERSION)
KUBECTL_VERSION = "v1.18.0"
KUBECTL_PATH = BASE_PATH + "/kubectl"
KUBECTL_RELEASE_URL = "https://storage.googleapis.com/kubernetes-release/release/{version}/bin/{operating_system}/amd64/kubectl".format(
    version=KUBECTL_VERSION, operating_system=platform.system().lower())
SPACE = " "
