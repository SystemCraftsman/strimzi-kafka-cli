import os
import stat
import wget
import tarfile
import ssl

from kfk.constants import *
from pathlib import Path
from setuptools import setup

ssl._create_default_https_context = ssl._create_unverified_context

if not os.path.exists(KUBECTL_PATH):
    print("Creating Strimzi Kafka CLI Dependencies folder if not exists: {base_path}".format(base_path=BASE_PATH))
    Path(BASE_PATH).mkdir(exist_ok=True)

    print("Downloading kubectl {version}...".format(version=KUBECTL_VERSION))
    wget.download(KUBECTL_RELEASE_URL, KUBECTL_PATH)
    os.chmod(KUBECTL_PATH, stat.S_IEXEC)

if not os.path.exists(STRIMZI_PATH):
    strimzi_tarfile_path = STRIMZI_PATH + ".tar.gz"

    print("Creating Strimzi Kafka CLI Dependencies folder if not exists: {base_path}".format(base_path=BASE_PATH))
    Path(BASE_PATH).mkdir(exist_ok=True)

    print("Downloading Strimzi {version}...".format(version=STRIMZI_VERSION))
    wget.download(STRIMZI_RELEASE_URL, strimzi_tarfile_path)
    print("\nExtracting Strimzi {version}...".format(version=STRIMZI_VERSION))
    tar = tarfile.open(strimzi_tarfile_path)
    tar.extractall(path=BASE_PATH)
    tar.close()
    print("Deleting {file} file".format(file=strimzi_tarfile_path))
    os.remove(strimzi_tarfile_path)

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name='strimzi-kafka-cli',
    version='0.1.0-alpha4',
    description="Command Line Interface for Strimzi Kafka Operator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['kfk'],
    package_dir={'kfk': 'kfk'},
    install_requires=[
        'Click',
        'PyYAML',
        'wget',
    ],
    entry_points='''
        [console_scripts]
        kfk=kfk.main:kfk
    ''',

    url="https://github.com/systemcraftsman/strimzi-kafka-cli",
    python_requires='>=3.5',
)
