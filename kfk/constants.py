from pathlib import Path

BASE_PATH = str(Path.home())
STRIMZI_VERSION = "0.18.0"
STRIMZI_PATH = BASE_PATH + "/strimzi-{version}"
STRIMZI_RELEASE_URL = "https://github.com/strimzi/strimzi-kafka-operator/releases/download/{version}/strimzi-{version}.tar.gz"
SPACE= " "