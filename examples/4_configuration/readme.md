# Topic, User and Broker configuration on Strimzi by using Strimzi Kafka CLI

Strimzi Kafka CLI enables users to describe, create, delete configurations of topics, users and brokers like you did with native Apache Kafka commands.

While `kfk configs` command can be used to change the configuration of these three entities, one can change relevant entities' configuration by using the following as well:

 `kfk topics --config/--delete-config` for adding and deleting configurations to topics.
 
 `kfk users --quota/--delete-quota` for managing quotas as a part of the configuration of it.
 
 `kfk clusters --config/--delete-config` for adding and deleting configurations to all brokers.
 
 In this example we will show you to do the configuration in both ways. So let's start with `topic` configuration.

## Topic Config

Describe config:
```shell
kfk configs --describe --entity-type topics --entity-name my-topic -c my-cluster -n kafka
```

Add one config:
```shell
kfk configs --alter --add-config min.insync.replicas=3 --entity-type topics --entity-name my-topic -c my-cluster -n kafka
```

Add two configs:
```shell
kfk configs --alter --add-config min.insync.replicas=3 --add-config cleanup.policy=compact --entity-type topics --entity-name my-topic -c my-cluster -n kafka
```

Delete one topic config:
```shell
kfk configs --alter --delete-config cleanup.policy=compact --entity-type topics --entity-name my-topic -c my-cluster -n kafka
```

## User Config

## Broker Config