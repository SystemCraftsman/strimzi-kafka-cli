# Simple ACL Authorization

In the previous example we implemented TLS authentication on Strimzi Kafka cluster with Strimzi Kafka CLI. In this example, we will be continuing with enabling the ACL authorization, so that we will be able to restrict access to our topics and only allow the users or groups we want to.

Let's first see our cluster list. 

```shell
kfk clusters --list
```
```
NAMESPACE    NAME              DESIRED KAFKA REPLICAS   DESIRED ZK REPLICAS
kafka        my-cluster        3                        3
```

---
**IMPORTANT**

You should have a cluster called `my-cluster` on the namespace `kafka` we created before. If you don't have the cluster and haven't yet done the authentication part please go back to the previous example and do it first since for authorization you will need authentication to be set up before. 

Also please copy the `truststore.jks` and the `user.p12` files or recreate them as explained in the previous example and put it along the example folder which we ignore in git.

---

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

and put the simple authorization definitions under `kafka` like the following:

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

As you might also observe, both the producer and consumer returned `TopicAuthorizationException` by saying `Not authorized to access topics: [my-topic]`. So let's define authorization access to this topic for the user `my-user`.

In order to enable user's authorization, we have to both define the user's authorization type as `simple` for it to use `SimpleAclAuthorizer` of Apache Kafka, and the ACL definitions for the relevant topic -in this case it is `my-topic`. To do this, we need to alter the user with the following command options: 

```shell
kfk users --alter --user my-user --authorization-type simple --add-acl --resource-type topic --resource-name my-topic -n kafka -c my-cluster
```

The `--add-acl` option requires arguments like:

```

--operation TEXT                Operation that is being allowed or denied.
                                  (default: All)

--host TEXT                     Host which User will have access. (default:
                              *)

--type [allow|deny]             Operation type for ACL. (default: allow)
--resource-type TEXT            This argument is mutually inclusive with
                              ['add_acl', 'delete_acl']

--resource-name TEXT            This argument is mutually inclusive with
                              ['add_acl', 'delete_acl']

```

In this example we only used `--resource-type` and `--resource-name` since those are the required fields and others have some defaults that we could use.

So in this case we used the defaults of `type:allow`, `host:*` and `operation:All`. The equal command should look like this:

```shell
kfk users --alter --user my-user --authorization-type simple --add-acl --resource-type topic --resource-name my-topic --type allow --host * --operation All -n kafka -c my-cluster
```

In order to see the ACL that is defined for allowing all operations of `my-topic` for the user `my-user`, let's describe it, in this case as YAML format: 

```shell
kfk users --describe --user my-user -n kafka -c my-cluster -o yaml
```

```
apiVersion: kafka.strimzi.io/v1beta1
kind: KafkaUser
metadata:
...
spec:
  authentication:
    type: tls
  authorization:
    type: simple
    acls:
    - host: '*'
      operation: All
      resource:
        name: my-topic
        patternType: literal
        type: topic
      type: allow
status:
...
```

As you can see the user has the authorization defined as `simple` and ACL that allows all (read, write, describe) access for `my-topic` from this user.

Now with the updated configuration let's run our producer and consumer again:

```shell
kfk console-producer --topic my-topic -n kafka -c my-cluster --producer.config client.properties
```

```
>message1
>message2
>message3
>
```

It seems that we are able to produce messages to `my-topic`. Let's consume those messages then:

```shell
kfk console-consumer --topic my-topic -n kafka -c my-cluster --consumer.config client.properties
```

```
ERROR Error processing message, terminating consumer process:  (kafka.tools.ConsoleConsumer$)
org.apache.kafka.common.errors.GroupAuthorizationException: Not authorized to access group: console-consumer-96150
Processed a total of 0 messages
```

Whoops! It did not work like the producer. But why? Because the consumer group that is randomly generated for us (because we did not define it anywhere) doesn't have at least `read` permission on `my-topic` topic. 

---
**IMPORTANT**

In Apache Kafka, if you want to consume messages you have to do it via a consumer group. You might say that "we did not specify any consumer group while using the console consumer". Well just like the traditional console consumer of Kafka, it uses a randomly created consumer group id so you have a consumer group but it is created for you (like the one above as `console-consumer-96150`) since we did not define one previously.

---

Ok then. Now let's add the ACL for a group in order to give `read` permission for `my-topic` topic. Let's call this group `my-group`, which we will also use it as the group id in our consumer client configuration. This time let's use `kfk acls` command which works like `kfk users --alter --add-acl` command. In order to give the best traditional experience to Strimzi CLI users, just like the traditional `bin/kafka-acls.sh` command, we have the `kfk acls` command which works mostly the same with the traditional one.

With the following command, we give the `my-group` group the `read` right for consuming the messages. 

```shell
kfk acls --add --allow-principal User:my-user --group my-group --operation Read -n kafka -c my-cluster
```

After adding the ACL, let's check whether our user has the ACL for the group or not:

```shell
kfk users --describe --user my-user -n kafka -c my-cluster -o yaml
```

In the `acls` section of the YAML you can see the entries are added:

```
    - host: '*'
      operation: Read
      resource:
        name: my-group
        patternType: literal
        type: group
      type: allow
```

You can list the ACLs with the following command as well which lists all the ACLs Kafka natively:

```shell
kfk acls --list -n kafka -c my-cluster
```

```
Current ACLs for resource `ResourcePattern(resourceType=GROUP, name=my-group, patternType=LITERAL)`:
 	(principal=User:CN=my-user, host=*, operation=READ, permissionType=ALLOW)

Current ACLs for resource `ResourcePattern(resourceType=TOPIC, name=my-topic, patternType=LITERAL)`:
 	(principal=User:CN=my-user, host=*, operation=ALL, permissionType=ALLOW)
```

Or you can list topic and group ACLs seperately:

```shell
kfk acls --list --topic my-topic -n kafka -c my-cluster
```

```
Current ACLs for resource `ResourcePattern(resourceType=TOPIC, name=my-topic, patternType=LITERAL)`:
 	(principal=User:CN=my-user, host=*, operation=ALL, permissionType=ALLOW)
```

For the group ACLs:

```shell
kfk acls --list --group my-group -n kafka -c my-cluster
```

```
Current ACLs for resource `ResourcePattern(resourceType=GROUP, name=my-group, patternType=LITERAL)`:
 	(principal=User:CN=my-user, host=*, operation=READ, permissionType=ALLOW)
```


The only thing we have to do right now is to put the group id definition in our `client.properties` file:

```
security.protocol=SSL
ssl.truststore.location=./truststore.jks
ssl.truststore.password=123456
ssl.keystore.location=./user.p12
ssl.keystore.password=123456
group.id=my-group
```

Running the consumer again with the updated client configuration -this time consuming from the beginning- let's see the previously produced logs: 

```shell
kfk console-consumer --topic my-topic -n kafka -c my-cluster --consumer.config client.properties --from-beginning
```

```
message1
message2
message3
```

Voilà!

We are able to configure the Strimzi cluster for ACL authorization, define ACLs easily with different methods and use the client configurations successfully with Strimzi Kafka CLI.


