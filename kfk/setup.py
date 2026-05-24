import os
import ssl
import tarfile
from pathlib import Path

import wget

from kfk.config import BASE_PATH, STRIMZI_PATH, STRIMZI_RELEASE_URL, STRIMZI_VERSION

ssl._create_default_https_context = ssl._create_unverified_context


def setup():
    download_strimzi_if_not_exists()


def download_strimzi_if_not_exists():
    if not os.path.exists(STRIMZI_PATH):
        strimzi_tarfile_path = STRIMZI_PATH + ".tar.gz"

        print(f"Creating Strimzi Kafka CLI Dependencies folder: {BASE_PATH}\n")
        Path(BASE_PATH).mkdir(exist_ok=True)

        print(f"Downloading dependency: Strimzi {STRIMZI_VERSION}...\n")
        wget.download(STRIMZI_RELEASE_URL, strimzi_tarfile_path)
        print("\nDownload successfully completed!\n")
        print(f"Extracting Strimzi {STRIMZI_VERSION}...\n")
        tar = tarfile.open(strimzi_tarfile_path)
        tar.extractall(path=BASE_PATH)
        tar.close()
        os.remove(strimzi_tarfile_path)
