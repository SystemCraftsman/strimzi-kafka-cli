from setuptools import setup
from post_setup import PostInstallCommand, PostDevelopCommand

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
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
)
