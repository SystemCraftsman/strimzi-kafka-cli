from pathlib import Path

STRIMZI_VERSION = "1.0.0"

BASE_FOLDER = ".strimzi-kafka-cli"
BASE_PATH = str(Path.home() / BASE_FOLDER)
STRIMZI_PATH = f"{BASE_PATH}/strimzi-{STRIMZI_VERSION}"
STRIMZI_RELEASE_URL = (
    f"https://github.com/strimzi/strimzi-kafka-operator/releases/"
    f"download/{STRIMZI_VERSION}/strimzi-{STRIMZI_VERSION}.tar.gz"
)
