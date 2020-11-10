from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name='strimzi-kafka-cli',
    version='0.1.0-alpha33',
    description="Command Line Interface for Strimzi Kafka Operator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['kfk'],
    package_dir={'kfk': 'kfk'},
    install_requires=[
        'Click==7.1.2',
        'PyYAML==5.3.1',
        'wget==3.2',
    ],
    entry_points='''
        [console_scripts]
        kfk=kfk.main:kfk
    ''',

    url="https://github.com/systemcraftsman/strimzi-kafka-cli",
    python_requires='>=3.5',
)
