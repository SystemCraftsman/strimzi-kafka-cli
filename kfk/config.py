import os
from pathlib import Path

STRIMZI_VERSION = "1.0.0"

BASE_FOLDER = ".strimzi-kafka-cli"
BASE_PATH = (
    (str(Path.home()) + "/" + BASE_FOLDER)
    if os.environ.get("STRIMZI_KAFKA_CLI_BASE_PATH") is None
    else os.environ.get("STRIMZI_KAFKA_CLI_BASE_PATH")
)
STRIMZI_PATH = (
    (BASE_PATH + f"/strimzi-{STRIMZI_VERSION}")
    if os.environ.get("STRIMZI_KAFKA_CLI_STRIMZI_PATH") is None
    else os.environ.get("STRIMZI_KAFKA_CLI_STRIMZI_PATH")
)
STRIMZI_RELEASE_URL = (
    f"https://github.com/strimzi/strimzi-kafka-operator/releases/"
    f"download/{STRIMZI_VERSION}/strimzi-{STRIMZI_VERSION}.tar.gz"
)
