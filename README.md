![Build](https://github.com/systemcraftsman/strimzi-kafka-cli/workflows/Build/badge.svg) ![Deploy](https://github.com/systemcraftsman/strimzi-kafka-cli/workflows/Deploy/badge.svg) ![PyPI](https://img.shields.io/pypi/v/strimzi-kafka-cli) [![Downloads](https://pepy.tech/badge/strimzi-kafka-cli)](https://pepy.tech/project/strimzi-kafka-cli)

![strimzi cli](https://raw.githubusercontent.com/systemcraftsman/strimzi-kafka-cli/master/logo/strimzi_cli.png)

# Strimzi Kafka CLI

Strimzi Kafka CLI is a CLI that helps traditional Apache Kafka users
-mostly administrators- to easily adapt [Strimzi](https://strimzi.io/),
a [Kubernetes
operator](https://operatorhub.io/operator/strimzi-kafka-operator) for
[Apache Kafka](https://kafka.apache.org/).

Intention here is to ramp up Strimzi usage by creating a similar CLI
experience with traditional Apache Kafka binaries.

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
  operator          Install/Uninstall Strimzi Kafka Operator
  topics            The kafka topic(s) to be created, altered or described.
  users             The kafka user(s) to be created, altered or described.
  version           Prints the version of Strimzi Kafka CLI
```

Please take a look at the relevant article [Strimzi Kafka CLI: Managing Strimzi in a Kafka Native Way](https://www.systemcraftsman.com/2020/08/25/strimzi-kafka-cli-managing-strimzi-in-a-kafka-native-way/) for more details.

## Installation

Strimzi Kafka CLI can be installed via pip (python package installer).

``` bash
sudo pip install strimzi-kafka-cli
```

Project requires: Python >=3.6

## Examples

* [TLS Authentication](https://github.com/systemcraftsman/strimzi-kafka-cli/tree/master/examples/2_tls_authentication)
* [Simple ACL Authorization](https://github.com/systemcraftsman/strimzi-kafka-cli/tree/master/examples/3_simple_acl_authorization)
* [Topic, User and Broker Configuration](https://github.com/systemcraftsman/strimzi-kafka-cli/tree/master/examples/4_configuration)

## Dependencies
### Python Dependencies
Please see [requirements.txt](https://github.com/systemcraftsman/strimzi-kafka-cli/blob/master/requirements.txt) file.
### External Dependencies
kubectl and Strimzi binaries are the tools that Strimzi Kafka CLI uses. These dependencies are automatically downloaded when the first `kfk` command is run. You can always check the dependency versions of your CLI with the following command:

``` bash
kfk version
```

If you want to change the `kubectl` and `Strimzi binaries`, you can simply change their version with the help of some environment veriables in order to let Strimzi Kafka CLI download the version you want, or change the PATH of any if you want to use a custom kubectl or Strimzi binary folder.

*STRIMZI_KAFKA_CLI_BASE_PATH:* Set this if you want to have a custom Strimzi Kafka CLI folder. It is set in `~/.strimzi-kafka-cli` as default.

*STRIMZI_KAFKA_CLI_STRIMZI_VERSION:* Set this if you want to use a different Strimzi version.

*STRIMZI_KAFKA_CLI_STRIMZI_PATH:* Set this if you want to use a custom Strimzi/AMQ Streams.

*STRIMZI_KAFKA_CLI_KUBECTL_VERSION* Set this if you want to use a different kubectl version.

*STRIMZI_KAFKA_CLI_KUBECTL_PATH:* Set this if you want to use a custom kubectl.
