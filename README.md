![Build](https://github.com/systemcraftsman/strimzi-kafka-cli/workflows/Build/badge.svg) ![Deploy](https://github.com/systemcraftsman/strimzi-kafka-cli/workflows/Deploy/badge.svg) [![PyPI](https://img.shields.io/pypi/v/strimzi-kafka-cli)](https://pypi.org/project/strimzi-kafka-cli/) [![Downloads](https://static.pepy.tech/badge/strimzi-kafka-cli)](https://pepy.tech/project/strimzi-kafka-cli) [![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0) [![Strimzi](https://img.shields.io/badge/Strimzi-0.40.0-blue)](https://github.com/strimzi/strimzi-kafka-operator/releases/tag/0.40.0) [![AMQ Streams](https://img.shields.io/badge/AMQ&nbsp;Streams-2.6.0-red)](https://access.redhat.com/documentation/en-us/red_hat_amq_streams/2.6)

![Strimzi CLI logo](https://github.com/SystemCraftsman/strimzi-kafka-cli/assets/10568159/596ea147-9594-4262-a0c3-d63fa14f0577)

# Strimzi Kafka CLI

Strimzi Kafka CLI is a CLI that helps traditional Apache Kafka users -both developers and administrators- to easily adapt to [Strimzi](https://strimzi.io/),
a [Kubernetes operator](https://operatorhub.io/operator/strimzi-kafka-operator) for [Apache Kafka](https://kafka.apache.org/).

The main intention is to ramp up Strimzi usage by creating a similar CLI experience with the traditional Apache Kafka tools that mostly starts with `kafka-*` prefix under the `bin` directory in an ordinary Kafka package.

Strimzi Kafka CLI uses the `kfk` command as an abbreviation for "**K**afka **F**or **K**ubernetes" or simply "**k** a **f** **k** a" which reminds of the `kafka-*` prefix of the ordinary Kafka script file names.

While having similar set of commands or options for some of the common objects, Strimzi Kafka CLI has some extra capabilities for managing or configuring Strimzi related resources.

Following are the commands of the current version of Strimzi Kafka CLI, that are used for different purposes:

``` bash
Usage: kfk [OPTIONS] COMMAND [ARGS]...

  Strimzi Kafka CLI

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  acls              Manages ACLs on Kafka.
  clusters          Creates, alters, deletes, describes Kafka cluster(s).
  configs           Adds/Removes entity config for a topic, client, user or...
  connect           Creates, alters, deletes, describes Kafka connect...
  console-consumer  Reads data from Kafka topics and outputs it to standard...
  console-producer  Reads data from standard input and publish it to Kafka.
  env               Prints the environment variable values for Strimzi Kafka CLI
  operator          Installs/Uninstalls Strimzi Kafka Operator
  topics            Creates, alters, deletes, describes Kafka topic(s).
  users             Creates, alters, deletes, describes Kafka users(s).
```

Please take a look at the relevant article [Strimzi Kafka CLI: Managing Strimzi in a Kafka Native Way](https://www.systemcraftsman.com/2020/08/25/strimzi-kafka-cli-managing-strimzi-in-a-kafka-native-way/) for more details.

## Installation

### Using Python Package Installer

``` bash
pip install strimzi-kafka-cli --user
```

Or to install Strimzi Kafka CLI in an isolated environment, you can simply use [pipx](https://pypa.github.io/pipx/):

``` bash
pipx install strimzi-kafka-cli
```

### Using Homebrew

``` bash
#Tap the homebrew repository first.
brew tap systemcraftsman/strimzi-kafka-cli

#Install Strimzi Kafka CLI
brew install strimzi-kafka-cli
```

> Installing the CLI by using Homebrew already uses a virtual environment, so you don't have to worry about your main Python environment.

Project requires: Python >=3.8

## Examples

* [TLS Authentication](https://github.com/systemcraftsman/strimzi-kafka-cli/tree/master/examples/2_tls_authentication)
* [Simple ACL Authorization](https://github.com/systemcraftsman/strimzi-kafka-cli/tree/master/examples/3_simple_acl_authorization)
* [Topic, User and Broker Configuration](https://github.com/systemcraftsman/strimzi-kafka-cli/tree/master/examples/4_configuration)
* [Kafka Connect](https://github.com/systemcraftsman/strimzi-kafka-cli/tree/master/examples/5_connect)

## Dependencies
### Python Dependencies
Please see [pyproject.toml](https://github.com/SystemCraftsman/strimzi-kafka-cli/blob/main/pyproject.toml) file.
### External Dependencies
`kubectl` and `Strimzi resources` are the tools that Strimzi Kafka CLI uses. These dependencies are automatically downloaded when the first `kfk` command is run. You can always check the dependency versions of your CLI with the following command:

``` bash
kfk --version
```

You can change where you want to locate the `kubectl`, `Strimzi resources`, or `Strimzi CLI` files/folders. You can use the following environment variables:

**STRIMZI_KAFKA_CLI_BASE_PATH:** Set this if you want to have a custom Strimzi Kafka CLI folder. It is `~/.strimzi-kafka-cli` as default.

**STRIMZI_KAFKA_CLI_STRIMZI_PATH:** Set this if you want to use a custom Strimzi/AMQ Streams. We only recommend this when using AMQ Streams instead of Strimzi.

**STRIMZI_KAFKA_CLI_KUBECTL_PATH:** Set this if you want to use a custom kubectl.
