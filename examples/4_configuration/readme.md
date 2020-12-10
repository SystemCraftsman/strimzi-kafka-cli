# Topic, User and Broker Configuration

Strimzi Kafka CLI enables users to describe, create, delete configurations of topics, users and brokers like you did with native Apache Kafka commands.

While `kfk configs` command can be used to change the configuration of these three entities, one can change relevant entities' configuration by using the following as well:

 * `kfk topics --config/--delete-config` for adding and deleting configurations to topics.
 
 * `kfk users --quota/--delete-quota` for managing quotas as a part of the configuration of it.
 
 * `kfk clusters --config/--delete-config` for adding and deleting configurations to all brokers.
 
 In this example we will show you to do the configuration in both ways. So let's start with `topic` configuration.

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

Now let's add a configuration like `min.insync.replicas`, which configures the sync replica count through the broker, between the leaders and followers. 
In order to add a configuration you must use `--alter` and for each config to be add `--add-config` following the `kfk config` command:


```shell
kfk configs --alter --add-config min.insync.replicas=3 --entity-type topics --entity-name my-topic -c my-cluster -n kafka
```

You should see a message like this:

```
kafkatopic.kafka.strimzi.io/my-topic configured
```

In order to add two configs -let's say that we wanted to add `cleanup.policy=compact` configuration along with `min.insync.replicas`- run a command like following: 

```shell
kfk configs --alter --add-config 'min.insync.replicas=3,cleanup.policy=compact' --entity-type topics --entity-name my-topic -c my-cluster -n kafka
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

Like adding a configuration, deleting a configuration is very easy. You can remove all the configurations that you've just set with a single command:

```shell
kfk configs --alter --delete-config 'min.insync.replicas,cleanup.policy'--entity-type topics --entity-name my-topic -c my-cluster -n kafka
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

## User Configuration

For the user configuration let's first create a user called `my-user`:

```shell
kfk users --create --user my-user --authentication-type tls  -n kafka -c my-cluster
```

After creating the user, let's add two configurations as quota configurations like `request_percentage=55` and `consumer_byte_rate=2097152`.

```shell
kfk configs --alter --add-config 'request_percentage=55,consumer_byte_rate=2097152' --entity-type users --entity-name my-user -c my-cluster -n kafka
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

You can see that empty response returning since there is no configuration anymore after the deletion:

```shell
kfk configs --describe --entity-type users --entity-name my-user -c my-cluster -n kafka --native
```

## Broker Configuration
