import os
import stat
import wget
import tarfile
import ssl

from kfk.config import *
from pathlib import Path

ssl._create_default_https_context = ssl._create_unverified_context


def setup():
    download_kubectl_if_not_exists()
    download_strimzi_if_not_exists()


def download_kubectl_if_not_exists():
    if not os.path.exists(KUBECTL_PATH):
        print(
            "Creating Strimzi Kafka CLI Dependencies folder: {base_path}\n".format(base_path=BASE_PATH))
        Path(BASE_PATH).mkdir(exist_ok=True)

        print("Downloading dependency: kubectl {version}...\n".format(version=KUBECTL_VERSION))
        wget.download(KUBECTL_RELEASE_URL, KUBECTL_PATH)
        print("\nDownload successfully completed!\n")
        current_stat = os.stat(KUBECTL_PATH)
        os.chmod(KUBECTL_PATH, current_stat.st_mode | stat.S_IEXEC)


def download_strimzi_if_not_exists():
    if not os.path.exists(STRIMZI_PATH):
        strimzi_tarfile_path = STRIMZI_PATH + ".tar.gz"

        print(
            "Creating Strimzi Kafka CLI Dependencies folder: {base_path}\n".format(base_path=BASE_PATH))
        Path(BASE_PATH).mkdir(exist_ok=True)

        print("Downloading dependency: Strimzi {version}...\n".format(version=STRIMZI_VERSION))
        wget.download(STRIMZI_RELEASE_URL, strimzi_tarfile_path)
        print("\nDownload successfully completed!\n")
        print("Extracting Strimzi {version}...\n".format(version=STRIMZI_VERSION))
        tar = tarfile.open(strimzi_tarfile_path)
        tar.extractall(path=BASE_PATH)
        tar.close()
        os.remove(strimzi_tarfile_path)
