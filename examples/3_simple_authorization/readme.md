# Simple ACL Authorization on Strimzi by using Strimzi Kafka CLI

In the previous example we implemented TLS authentication on Strimzi Kafka cluster with Strimzi Kafka CLI. In this example, we will be continuing with enabling the ACL authorization, so that we will be able to restrict access to our topics and only allow the users or groups we want to.

Let's first see our cluster list. 

```shell
kfk clusters --list
```

You should have a cluster called `my-cluster` on the namespace `kafka` we created before. If you don't have the cluster and haven't yet done the authentication part please go back to the previous example and do it first since for authorization you will need authentication to be set up before.

```
NAMESPACE    NAME              DESIRED KAFKA REPLICAS   DESIRED ZK REPLICAS
kafka        my-cluster        3                        3
```

Considering you have the cluster `my-cluster` on namespace `kafka`, let's list our topics to see the topic we created before:

```shell
kfk topics --list -n kafka -c my-cluster
```

```
NAME                                                          PARTITIONS   REPLICATION FACTOR
consumer-offsets---84e7a678d08f4bd226872e5cdd4eb527fadc1c6a   50           3
my-topic                                                      12           3
```

Lastly let's list our user that we created previously, which we will be setting the authorization for.

```shell
kfk users --list -n kafka -c my-cluster
```

```
NAME      AUTHENTICATION   AUTHORIZATION
my-user   tls
```

As you can see we have the `my-user` user that we created and authenticated in the previous example.

Now let's configure our cluster to enable for ACL authorization. We have to alter our cluster for this: 

```shell
kfk clusters --alter --cluster my-cluster -n kafka
```

and put the simple authorization definitions under kafka's `spec` like the following:

```yaml
authorization:
  type: simple
```

After saving the cluster configuration wait for the brokers to be rolling updated by checking their status:

```shell
watch kubectl get pods -n kafka
```

Now it's time to run the producer and consumer to check if authorization is enabled:

```shell
kfk console-producer --topic my-topic -n kafka -c my-cluster --producer.config client.properties
```

```
ERROR Error when sending message to topic my-topic with key: null, value: 4 bytes with error: (org.apache.kafka.clients.producer.internals.ErrorLoggingCallback)
org.apache.kafka.common.errors.TopicAuthorizationException: Not authorized to access topics: [my-topic]
```

```shell
kfk console-consumer --topic my-topic -n kafka -c my-cluster --consumer.config client.properties
```

```
ERROR Error processing message, terminating consumer process:  (kafka.tools.ConsoleConsumer$)
org.apache.kafka.common.errors.TopicAuthorizationException: Not authorized to access topics: [my-topic]
Processed a total of 0 messages
```

```shell
kfk users --alter --user my-user --authorization-type simple --add-acl --resource-type topic --resource-name my-topic -n kafka -c my-cluster
```

```shell
kfk users --describe --user my-user -n kafka -c my-cluster -o yaml
```

```shell
kfk console-producer --topic my-topic -n kafka -c my-cluster --producer.config client.properties
```

```
>message1
>message2
>message3
>
```

```shell
kfk console-consumer --topic my-topic -n kafka -c my-cluster --consumer.config client.properties
```

```
ERROR Error processing message, terminating consumer process:  (kafka.tools.ConsoleConsumer$)
org.apache.kafka.common.errors.GroupAuthorizationException: Not authorized to access group: console-consumer-96150
Processed a total of 0 messages
```

```shell
kfk acls --add --allow-principal User:my-user --group my-group --operation Read -n kafka -c my-cluster
```

```shell
kfk console-consumer --topic my-topic -n kafka -c my-cluster --consumer.config client.properties --from-beginning
```
