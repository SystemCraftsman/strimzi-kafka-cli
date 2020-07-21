![Build](https://github.com/systemcraftsman/strimzi-kafka-cli/workflows/Build/badge.svg) ![Deploy](https://github.com/systemcraftsman/strimzi-kafka-cli/workflows/Deploy/badge.svg) [![PyPI version](https://badge.fury.io/py/strimzi-kafka-cli.svg)](https://badge.fury.io/py/strimzi-kafka-cli)

![strimzi cli](https://raw.githubusercontent.com/systemcraftsman/strimzi-kafka-cli/master/logo/strimzi_cli.png)

# Strimzi Kafka CLI

Strimzi Kafka CLI is a CLI that helps traditional Apache Kafka users
-mostly administrators- to easily adapt [Strimzi](https://strimzi.io/),
a [Kubernetes
operator](https://operatorhub.io/operator/strimzi-kafka-operator) for
[Apache Kafka](https://kafka.apache.org/).

Intention here is to ramp up Strimzi usage by creating a similar CLI
experience with traditional Apache Kafka binaries. For example:

| Native Command                             | Strimzi CLI Command  |
| ------------------------------------------ | -------------------- |
| $KAFKA\_HOME/bin/kafka-topics.sh           | kfk topics           |
| $KAFKA\_HOME/bin/kafka-configs.sh          | kfk configs          |
| $KAFKA\_HOME/bin/kafka-console-consumer.sh | kfk console-consumer |
| ... | ... |

**kfk** command stands for the usual **kafka-**\* prefix of the
Apache Kafka runnable files which are located in *bin* directory. There
are options provided like *topics*, *console-consumer*, etc. which also
mostly stand for the rest of the runnable file names like
*kafka-topic.sh*.

However, because of the nature of Strimzi and its capabilities, there
are also unusual options like *clusters* which is used for
cluster configuration or *users* which is used for user management and
configuration.

Following is the high-level output of the Strimzi Kafka CLI:

``` bash
Usage: kfk [OPTIONS] COMMAND [ARGS]...

  Strimzi Kafka CLI

Options:
  --help  Show this message and exit.

Commands:
  acls              This tool helps to manage ACLs on Kafka.
  clusters          The kafka cluster(s) to be created, altered or...
  configs           Add/Remove entity config for a topic, client, user or...
  console-consumer  The console consumer is a tool that reads data from...
  console-producer  The console producer is a tool that reads data from...
  topics            The kafka topic(s) to be created, altered or described.
  users             The kafka user(s) to be created, altered or described.
  version           Prints the version of Strimzi Kafka CLI
```

## Installation

Strimzi Kafka CLI can be installed via pip (python package installer).

``` bash
pip install strimzi-kafka-cli
```
Project requires: Python >=3.5

## Dependencies
### Python Dependencies
Please see [requirements.txt](https://github.com/systemcraftsman/strimzi-kafka-cli/blob/master/requirements.txt) file.
### External Dependencies
- kubectl: kfk will automatically download kubectl binary which is configurable to use which kubectl version to use. (Pls see [issue-19](https://github.com/systemcraftsman/strimzi-kafka-cli/issues/19))
- Strimzi binaries: kfk will download it automatically. The yaml templates are used for create actions. This is configurable to use which binaries path to use. (Pls see [issue-19](https://github.com/systemcraftsman/strimzi-kafka-cli/issues/19))


More info will be added soon.
