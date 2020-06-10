from setuptools import setup

with open("README.adoc", "r") as file:
    long_description = file.read()

setup(
    name='strimzi-kafka-cli',
    version='0.1.0-rc1',
    description="Command Line Interface for Strimzi Kafka Operator",
    long_description=long_description,
    long_description_content_type="text/asciidoc",
    py_modules=['strimzi_kafka_cli'],
    install_requires=[
        'Click',
        'PyYAML',
        'wget',
    ],
    entry_points='''
        [console_scripts]
        kfk=strimzi_kafka_cli:kfk
    ''',

    url="https://github.com/systemcraftsman/strimzi-kafka-cli",
    python_requires='>=3.7',
)
