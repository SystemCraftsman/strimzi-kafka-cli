# Kafka Connect

---
**WARNING**

This example is under development

---

<!---
Prereqs: a namespace named `kafka` and a kafka cluster called `my-cluster`
-->

<!--- 
Show them the connector configs here, then create needed the topics
-->

```shell
kfk topics --create --topic twitter-status-connect --partitions 3 --replication-factor 1 -c my-cluster -n kafka
```

```shell
kfk topics --create --topic twitter-deletes-connect --partitions 3 --replication-factor 1 -c my-cluster -n kafka

```


<!--- 
Dont run this, just show them how it works. run the next
-->
```shell
kfk connect clusters --create --cluster my-connect-cluster --replicas 1 -n mabulgu-kafka-cluster connect.properties twitter_connector.properties
```


```shell
kfk connect clusters --create --cluster my-connect-cluster --replicas 1 -n mabulgu-kafka-cluster connect.properties twitter_connector.properties -y
```

```
secret/my-connect-cluster-push-secret created
kafkaconnect.kafka.strimzi.io/my-connect-cluster created
kafkaconnector.kafka.strimzi.io/twitter-source-demo created
```


```shell
watch kubectl get pods -n kafka
```

```
...output omitted...
my-connect-cluster-connect-8444df69c9-x7xf6   1/1     Running     0          3m43s
...output omitted...
```

<!--- 
Show them the tweet stream by consuming the twitter-status-connect topic
-->

```shell
kfk console-consumer --topic twitter-status-connect -c my-cluster -n kafka
```
