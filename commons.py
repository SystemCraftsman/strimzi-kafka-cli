import click
import os
import wget
import tarfile
import ssl

from constants import *

ssl._create_default_https_context = ssl._create_unverified_context

@click.group()
def kfk():
    """Strimzi CLI"""


def download_strimzi_if_not_exists():
    if not os.path.exists(STRIMZI_PATH.format(version=STRIMZI_VERSION)):
        strimzi_tarfile_path = STRIMZI_PATH.format(version=STRIMZI_VERSION) + ".tar.gz"

        print("Strimzi files are not available. Downloading Strimzi {version}...".format(version=STRIMZI_VERSION))
        wget.download(STRIMZI_RELEASE_URL.format(version=STRIMZI_VERSION), strimzi_tarfile_path)
        print("\nExtracting Strimzi {version}...".format(version=STRIMZI_VERSION))
        tar = tarfile.open(strimzi_tarfile_path)
        tar.extractall(path=BASE_PATH)
        tar.close()
        print("Deleting {file} file".format(file=strimzi_tarfile_path))
        os.remove(strimzi_tarfile_path)


def print_missing_options_for_command(command_str):
    print("Missing options: kfk {command_str} [OPTIONS] \n Try 'kfk {command_str} --help' for help.".format(
        command_str=command_str))


def delete_last_applied_configuration(dict):
    if "annotations" in dict["metadata"]:
        del dict["metadata"]["annotations"]["kubectl.kubernetes.io/last-applied-configuration"]
