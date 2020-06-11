from setuptools import setup
from post_setup import download_strimzi_if_not_exists, download_kubectl_if_not_exists

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name='strimzi-kafka-cli',
    version='0.1.0-alpha5',
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

download_kubectl_if_not_exists()
download_strimzi_if_not_exists()
