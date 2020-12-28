# Topic, User and Broker Configuration

Strimzi Kafka CLI enables users to describe, create, delete configurations of topics, users and brokers like you did with native Apache Kafka commands.

While `kfk configs` command can be used to change the configuration of these three entities, one can change relevant entities' configuration by using the following as well:

 * `kfk topics --config/--delete-config` for adding and deleting configurations to topics.
 
 * `kfk users --quota/--delete-quota` for managing quotas as a part of the configuration of it.
 
 * `kfk clusters --config/--delete-config` for adding and deleting configurations to all brokers.
 
 In this example we will show you to do the configuration by using `kfk configs` only but will mention about the options above. 
 So let's start with `topic` configuration.

## Topic Configuration

Considering we already have a Kafka cluster called `my-cluster` on our namespace called `kafka`, let's create a topic on it called `my-topic`:

```shell
kfk topics --create --topic my-topic --partitions 12 --replication-factor 3 -c my-cluster -n kafka
```

---
**IMPORTANT**

If you don't have any Kafka cluster that is created on your OpenShift/Kubernetes, you can use the following command:

```shell
kfk clusters --create --cluster my-cluster -n kafka
```

You can easily create an operator on the current OpenShift/Kubernetes before creating a Kafka cluster if you don't have one:

```shell
kfk operator --install -n kafka
```

---

First let's see what pre-defined configurations we have on our topic:

```shell
kfk configs --describe --entity-type topics --entity-name my-topic -c my-cluster -n kafka --native
```

Since we are running our `config --describe` command with `--native` flag, we can see all the default dynamic configurations for the topic:

```
Dynamic configs for topic my-topic are:
  segment.bytes=1073741824 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:segment.bytes=1073741824, DEFAULT_CONFIG:log.segment.bytes=1073741824}
  retention.ms=7200000 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:retention.ms=7200000}
```

---
**INFO**

Additionally you can describe all of the topic configurations natively on current cluster. 
To do this, just remove the `entity-name` option:

```shell
kfk configs --describe --entity-type topics -c my-cluster -n kafka --native
```
---

We can also describe the `Topic` custom resource itself by removing the `--native` flag:

```shell
kfk configs --describe --entity-type topics --entity-name my-topic -c my-cluster -n kafka
```

```
...
Spec:
  Config:
    retention.ms:   7200000
    segment.bytes:  1073741824
...
```

Now let's add a configuration like `min.insync.replicas`, which configures the sync replica count through the broker, between the leaders and followers. 
In order to add a configuration you must use `--alter` and for each config to be add `--add-config` following the `kfk config` command:


```shell
kfk configs --alter --add-config min.insync.replicas=3 --entity-type topics --entity-name my-topic -c my-cluster -n kafka
```

You should see a message like this:

```
kafkatopic.kafka.strimzi.io/my-topic configured
```

Alternatively you can set the topic configuration by using `kfk topics` with `--config` option:

```shell
kfk topics --alter --topic my-topic --config min.insync.replicas=3 -c my-cluster -n kafka
```

In order to add two configs -let's say that we wanted to add `cleanup.policy=compact` configuration along with `min.insync.replicas`- run a command like following: 

```shell
kfk configs --alter --add-config 'min.insync.replicas=3,cleanup.policy=compact' --entity-type topics --entity-name my-topic -c my-cluster -n kafka
```

or

```shell
kfk topics --alter --topic my-topic --config min.insync.replicas=3 --config cleanup.policy=compact -c my-cluster -n kafka
```

After setting the configurations in order to see the changes, use the `--describe` flag like we did before:

```shell
kfk configs --describe --entity-type topics --entity-name my-topic -c my-cluster -n kafka --native
```

Output is:

```
Dynamic configs for topic my-topic are:
  min.insync.replicas=3 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:min.insync.replicas=3, DEFAULT_CONFIG:min.insync.replicas=1}
  cleanup.policy=compact sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:cleanup.policy=compact, DEFAULT_CONFIG:log.cleanup.policy=delete}
  segment.bytes=1073741824 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:segment.bytes=1073741824, DEFAULT_CONFIG:log.segment.bytes=1073741824}
  retention.ms=7200000 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:retention.ms=7200000}
```

In order to see the added configuration as a Strimzi resource run the same command without `--native` option:

```shell
kfk configs --describe --entity-type topics --entity-name my-topic -c my-cluster -n kafka
```

```
...
  Config:
    cleanup.policy:       compact
    min.insync.replicas:  3
    retention.ms:         7200000
    segment.bytes:        1073741824
...
```

Like adding a configuration, deleting a configuration is very easy. You can remove all the configurations 
that you've just set with a single command:

```shell
kfk configs --alter --delete-config 'min.insync.replicas,cleanup.policy' --entity-type topics --entity-name my-topic -c my-cluster -n kafka
```

or you can use:

```shell
kfk topics --alter --topic my-topic --delete-config min.insync.replicas --delete-config cleanup.policy -c my-cluster -n kafka
```

When you run the `describe` command again you will see that the relevant configurations are removed:

```shell
kfk configs --describe --entity-type topics --entity-name my-topic -c my-cluster -n kafka --native
```

```
Dynamic configs for topic my-topic are:
  segment.bytes=1073741824 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:segment.bytes=1073741824, DEFAULT_CONFIG:log.segment.bytes=1073741824}
  retention.ms=7200000 sensitive=false synonyms={DYNAMIC_TOPIC_CONFIG:retention.ms=7200000}
```

As you can see we could easily manipulate the topic configurations almost like the native shell 
executables of Apache Kafka. Now let's see how it is done for user configuration.

## User Configuration

For the user configuration let's first create a user called `my-user`:

```shell
kfk users --create --user my-user --authentication-type tls  -n kafka -c my-cluster
```

After creating the user, let's add two configurations as quota configurations like `request_percentage=55` and `consumer_byte_rate=2097152`.

```shell
kfk configs --alter --add-config 'request_percentage=55,consumer_byte_rate=2097152' --entity-type users --entity-name my-user -c my-cluster -n kafka
```

Alternatively you can set the user quota configuration by using `kfk users` with `--quota` option:

```shell
kfk users --alter --user my-user --quota request_percentage=55 --quota consumer_byte_rate=2097152 -c my-cluster -n kafka
```

---
**IMPORTANT**

In traditional `kafka-configs.sh` command there are actually 5 configurations, 3 of which are quota related ones:

```
consumer_byte_rate                    
producer_byte_rate                    
request_percentage  
```

and the other 2 is for authentication type:

```
SCRAM-SHA-256                         
SCRAM-SHA-512 
```

While these two configurations are also handled by `kafka-configs.sh` in traditional Kafka usage, 
in Strimzi CLI they are configured by altering the cluster by running the `kfk clusters --alter` 
command and altering the user by using the `kfk users --alter` command for adding the relevant authentication type. 
So `kfk configs` command will not be used for these two configurations since it's not supported.

---

Now let's take a look at the configurations we just set:

```shell
kfk configs --describe --entity-type users --entity-name my-user -c my-cluster -n kafka --native
```

```
Configs for user-principal 'CN=my-user' are consumer_byte_rate=2097152.0, request_percentage=55.0
```

---
**INFO**

Additionally you can describe all of the user configurations natively on current cluster. 
To do this, just remove the `entity-name` option:

```shell
kfk configs --describe --entity-type users -c my-cluster -n kafka --native
```
---

You can also see the changes in the Kubernetes native description:

```shell
kfk configs --describe --entity-type users --entity-name my-user -c my-cluster -n kafka
```

```
...
Spec:
...
  Quotas:
    Consumer Byte Rate:  2097152
    Request Percentage:  55
...
```

Deletion of the configurations is almost the same as deleting the topic configurations:

```shell
kfk configs --alter --delete-config 'request_percentage,consumer_byte_rate' --entity-type users --entity-name my-user -c my-cluster -n kafka
```

or

```shell
kfk users --alter --user my-user --delete-quota request_percentage=55 --delete-quota consumer_byte_rate=2097152 -c my-cluster -n kafka
```

You can see that empty response returning since there is no configuration anymore after the deletion:

```shell
kfk configs --describe --entity-type users --entity-name my-user -c my-cluster -n kafka --native
```

So we could easily update/create/delete the user configurations for Strimzi, almost like the native shell 
executables of Apache Kafka. Now let's take our final step to see how it is done for broker configuration.

## Broker Configuration

Adding configurations either as dynamic ones or static ones are as easy as it is for the topics and users.
For both configuration types, Strimzi takes care about it itself by rolling update the brokers for the static 
configurations and reflecting directly the dynamic configurations.

Here is a way to add a static configuration that will be reflected after the rolling update of the brokers:

```shell
kfk configs --alter --add-config log.retention.hours=168 --entity-type brokers --entity-name my-cluster -c my-cluster -n kafka
```

or alternatively using the `kfk clusters` command:

```shell
kfk clusters --alter --cluster my-cluster --config log.retention.hours=168 -n kafka
```

---
**IMPORTANT**

Unlike the native `kafka-configs` command, for the `entity-name` the Kafka cluster name should be set rather than the 
broker ids. In this 

---

```shell
kfk configs --describe --entity-type brokers --entity-name my-cluster -c my-cluster -n kafka
```

```
...
  Kafka:
    Config:
      log.message.format.version:                2.6
      log.retention.hours:                       168
      offsets.topic.replication.factor:          3
      transaction.state.log.min.isr:             2
      transaction.state.log.replication.factor:  3
...
```

You can describe the cluster config Kafka natively like the following:

```shell
kfk configs --describe --entity-type brokers -c my-cluster -n kafka --native
```

```
Dynamic configs for broker 0 are:
Dynamic configs for broker 1 are:
Dynamic configs for broker 2 are:
Default configs for brokers in the cluster are:

All user provided configs for brokers in the cluster are:
log.message.format.version=2.6
log.retention.hours=168
offsets.topic.replication.factor=3
transaction.state.log.min.isr=2
transaction.state.log.replication.factor=3
```

---
**IMPORTANT**

Note that using describe with `native` flag doesn't require any `entity-name` option since it fetches the cluster-wide
broker configuration. For a specific broker configuration one can set `entity-name` as the broker id which will only show
the first broker's configuration which will be totally the same with the cluster-wide one.

---

Now let's add a dynamic configuration in order to see it while describing with `native` flag. 
We will change `log.cleaner.threads` configuration which is responsible for controlling the background threads 
that do log compaction and is 1 one by default.

```shell
kfk configs --alter --add-config log.cleaner.threads=2 --entity-type brokers --entity-name my-cluster -c my-cluster -n kafka
```

or

```shell
kfk clusters --alter --cluster my-cluster --config log.cleaner.threads=2 -n kafka
```

While describing it via Strimzi custom resources will return you the list again:

```shell
kfk configs --describe --entity-type brokers --entity-name my-cluster -c my-cluster -n kafka
```

```
...
  Kafka:
    Config:
      log.cleaner.threads:                       2
      log.message.format.version:                2.6
      log.retention.hours:                       168
      offsets.topic.replication.factor:          3
      transaction.state.log.min.isr:             2
      transaction.state.log.replication.factor:  3
...
```

Describing it with `native` flag will give more details about configurations' being dynamic or not:

```shell
kfk configs --describe --entity-type brokers -c my-cluster -n kafka --native
```

```
Dynamic configs for broker 0 are:
  log.cleaner.threads=2 sensitive=false synonyms={DYNAMIC_BROKER_CONFIG:log.cleaner.threads=2, DEFAULT_CONFIG:log.cleaner.threads=1}
Dynamic configs for broker 1 are:
  log.cleaner.threads=2 sensitive=false synonyms={DYNAMIC_BROKER_CONFIG:log.cleaner.threads=2, DEFAULT_CONFIG:log.cleaner.threads=1}
Dynamic configs for broker 2 are:
  log.cleaner.threads=2 sensitive=false synonyms={DYNAMIC_BROKER_CONFIG:log.cleaner.threads=2, DEFAULT_CONFIG:log.cleaner.threads=1}
Default configs for brokers in the cluster are:

All user provided configs for brokers in the cluster are:
log.cleaner.threads=2
log.message.format.version=2.6
log.retention.hours=168
offsets.topic.replication.factor=3
transaction.state.log.min.isr=2
transaction.state.log.replication.factor=3
```

Deleting the configurations are exactly the same with the topics and users:

```shell
kfk configs --alter --delete-config 'log.retention.hours,log.cleaner.threads' --entity-type brokers --entity-name my-cluster -c my-cluster -n kafka
```

or use the following command:

```shell
kfk clusters --alter --cluster my-cluster --delete-config log.retention.hours --delete-config log.cleaner.threads -n kafka
```

You can see only initial configurations after the deletion:

```shell
kfk configs --describe --entity-type brokers -c my-cluster -n kafka --native
```

```
Dynamic configs for broker 0 are:
Dynamic configs for broker 1 are:
Dynamic configs for broker 2 are:
Default configs for brokers in the cluster are:

All user provided configs for brokers in the cluster are:
log.message.format.version=2.6
offsets.topic.replication.factor=3
transaction.state.log.min.isr=2
transaction.state.log.replication.factor=3
```

So that's all! 

We are able to create, update, delete the configurations of topics, users and Kafka cluster itself and describe the changed 
configurations both Kubernetes and Kafka natively using Strimzi Kafka CLI.