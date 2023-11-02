import os
import ssl
import stat
import subprocess
import tarfile
from pathlib import Path

import wget

from kfk.config import (
    BASE_PATH,
    KUBECTL_PATH,
    KUBECTL_RELEASE_URL,
    KUBECTL_VERSION,
    STRIMZI_PATH,
    STRIMZI_RELEASE_URL,
    STRIMZI_VERSION,
)
from kfk.kubectl_command_builder import Kubectl

ssl._create_default_https_context = ssl._create_unverified_context


def setup():
    download_kubectl_if_not_exists()
    update_kubectl_if_new_version_exists()
    download_strimzi_if_not_exists()


def download_kubectl_if_not_exists():
    if not os.path.exists(KUBECTL_PATH):
        print(f"Creating Strimzi Kafka CLI Dependencies folder: {BASE_PATH}\n")
        Path(BASE_PATH).mkdir(exist_ok=True)

        _download_kubectl()


def update_kubectl_if_new_version_exists():
    if (
        os.path.exists(KUBECTL_PATH)
        and os.environ.get("STRIMZI_KAFKA_CLI_KUBECTL_VERSION") is None
        and os.environ.get("STRIMZI_KAFKA_CLI_KUBECTL_PATH") is None
        and KUBECTL_VERSION
        not in subprocess.check_output(
            Kubectl().version("--client=true").build(),
            shell=True,
            stderr=subprocess.STDOUT,
        ).decode("utf-8")
    ):
        os.rename(KUBECTL_PATH, KUBECTL_PATH + "_old")
        _download_kubectl()


def _download_kubectl():
    print(f"Downloading dependency: kubectl {KUBECTL_VERSION}...\n")
    wget.download(KUBECTL_RELEASE_URL, KUBECTL_PATH)
    print("\nDownload successfully completed!\n")
    current_stat = os.stat(KUBECTL_PATH)
    os.chmod(KUBECTL_PATH, current_stat.st_mode | stat.S_IEXEC)


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
