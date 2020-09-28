# TLS Authentication on Strimzi by using Strimzi Kafka CLI

In this example we will demonstrate setting up TLS authentication for Strimzi using Strimzi Kafka CLI. So let's get started!


First lets list the clusters and see our clusters list.

```shell
kfk clusters --list
```
    
---
**IMPORTANT**

If you don't have any Kafka cluster that is created on your OpenShift/Kubernetes, pls. see the [Strimzi Quick Start](https://strimzi.io/quickstarts/) document or simply use:

```shell
kfk clusters --create -n kafka
```

---


Assuming we have a cluster called `my-cluster` already set up for us let's list the topics in the cluster

```shell
kfk topics --list -n kafka -c my-cluster
```

If it is a new cluster probably there is no topic living in the cluster yet. So let's create a new topic for our example.

Create a topic called `my-topic` with 12 partitions and replication
factor 3 in `my-cluster` cluster

```shell
kfk topics --create --topic my-topic --partitions 12 --replication-factor 3 -n kafka -c my-cluster
```

Run console producer to produce messages to `my-topic`

```shell
kfk console-producer --topic my-topic -n kafka -c my-cluster
```

Run console consumer to consume messages from `my-topic`

```shell
kfk console-consumer --topic my-topic -n kafka -c my-cluster
```

After being sure to produce and consume messages without a problem, now lets enable the authentication for TLS. In Strimzi, if you want to
enable authentication, there are listeners configurations that provides
a couple of authentication methodologies like `scram-sha-512`, `oauth`
and `tls`.

In order to enable the authentication we have to alter our Kafka
cluster:

```shell
kfk clusters --alter --cluster my-cluster -n kafka
```

An editor will be opened in order to change the Strimzi Kafka cluster
configuration. Since Strimzi Kafka cluster resource has many items
inside, for now, we don’t have any special property flag in order to
directly set the value while altering. That’s why we only open the
cluster custom resource available for editing.

In the opened editor we have to add the following listeners as:

```yaml
listeners:
  plain: {}
  tls:
    authentication:
      type: tls
```

If you want to fully secure your cluster you have to also change the
plain listener for authentication, because with the upper configuration
unless we use a client configuration that doesn’t use SSL security
protocol it will use the plain one which doesn’t require any
authentication. In order to do that, we can tell the plain listener in
cluster config to use one of the authentication methodologies among
`scram-sha-512` or `oauth`. In this example we will set it as
`scram-sha-512` but we will show the authentication via `scram-sha-512`
in another example.

So the latest listener definition should be like this:

```yaml
listeners:
  plain:
    authentication:
      type: scram-sha-512
  tls:
    authentication:
      type: tls
```

Save the file and see the successfully edited message.

After the configuration change all the broker pods will be updated one
by one, thanks to our operator. You can watch the pods state since we
have to wait till each of them are in `ready` state.

```shell
watch kubectl get pods -n kafka
```

Now lets run our console producer and consumer again and see what
happens:

```shell
kfk console-producer --topic my-topic -n kafka -c my-cluster
```

```shell
kfk console-consumer --topic my-topic -n kafka -c my-cluster
```

You got some WARN log messages saying `disconnected (org.apache.kafka.clients.NetworkClient)` from both
producer and consumer right?

When we check the first pod logs that we ran the producer and consumer
commands we can see the failed authentication message:

```shell
kubectl logs -f my-cluster-kafka-0 -c kafka -n kafka
```

    2020-09-22 11:18:33,122 INFO [SocketServer brokerId=0] Failed authentication with /10.130.2.58 (Unexpected Kafka request of type METADATA during SASL handshake.) (org.apache.kafka.common.network.Selector) [data-plane-kafka-network-thread-0-ListenerName(PLAIN-9092)-SASL_PLAINTEXT-3]

Since we are not yet using SSL for authentication, but the PLAIN
connection method, which we set up as `scram-sha-512`, we can not
authenticate to the Strimzi Kafka cluster.

In order to login this cluster via SSL authentication we have to;

* Create a user that uses TLS authentication
* Create truststore and keystore files by getting the certificates from Openshift/Kubernetes cluster
* Create a client.properties file that is to be used by producer and consumer clients in order to be able to authenticate via TLS

Let's first create the user with the name `my-user`:

```shell
kfk users --create --user my-user --authentication-type tls -n kafka -c my-cluster
```

After creating the user let's describe it to view a few attributes:

```shell
kfk users --describe --user my-user -n kafka -c my-cluster
```
At the bottom of the details of the user; in the status section, you can see a secret and a username definition:

```
Name:         my-user
Namespace:    kafka
Labels:       strimzi.io/cluster=my-cluster
Annotations:  <none>
API Version:  kafka.strimzi.io/v1beta1
Kind:         KafkaUser
Metadata:
  Creation Timestamp:  2020-09-21T12:54:52Z
  Generation:          3
  Resource Version:    53996010
  Self Link:           /apis/kafka.strimzi.io/v1beta1/namespaces/kafka/kafkausers/my-user
  UID:                 1c1dad0c-4e7a-4e63-933c-a785e6941021
Spec:
  Authentication:
    Type:  tls
Status:
  Observed Generation:     3
  Secret:                  my-user
  Username:                CN=my-user
Events:                    <none>
```

This means that a secret named `my-user` is created for this user and with the username `CN=my-user` as a common name definition.

In the secrets there are private and public keys that should be imported in the truststore and the keystore files that will be created shortly.

```shell
kubectl describe secret/my-user -n kafka
```

```
Name:         my-user
Namespace:    kafka
Labels:       app.kubernetes.io/instance=my-user
              app.kubernetes.io/managed-by=strimzi-user-operator
              app.kubernetes.io/name=strimzi-user-operator
              app.kubernetes.io/part-of=strimzi-my-user
              strimzi.io/cluster=my-cluster
              strimzi.io/kind=KafkaUser
Annotations:  <none>

Type:  Opaque

Data
====
ca.crt:         1164 bytes
user.crt:       1009 bytes
user.key:       1704 bytes
user.p12:       2364 bytes
user.password:  12 bytes
```

In order create the truststore and keystore files just run the get_keys.sh file in the [example directory](https://github.com/systemcraftsman/strimzi-kafka-cli/blob/master/examples/2_tls_authentication/get_keys.sh):

```shell
chmod a+x ./get_keys.sh;./get_keys.sh 
```

This will generate two files:

* `truststore.jks` for the client's truststore definition
* `user.p12` for the client's keystore definition

TLS authentications are made with bidirectional TLS handshake. In order to do this apart from a truststore that has the public key imported, a keystore file that has both the public and private keys has to be created and defined in the client configuration file.

So let's create our client configuration file. 

Our client configuration should have a few definitions like:

* Security protocol
* Truststore location and password
* Keystore location and password

Security protocol should be `SSL` and since the truststore and keystore files are located in the example directory the client config file should be something like this:

```properties
security.protocol=SSL
ssl.truststore.location=./truststore.jks
ssl.truststore.password=123456
ssl.keystore.location=./user.p12
ssl.keystore.password=123456
```

Since the `get_keys.sh` script sets the store passwords as `123456` we use it in the config file.

Save it as client.properties (or just use the one that is already created in this directory with the name `client.properties`)

Now it's time to test it. Let's call the console producer and consumer again, but this time with the client configuration:

---
**IMPORTANT**

Be careful to run producer and consumer commands from example's directory. Otherwise you have to change the truststore and keystore paths in the client.properties file.

---

```shell
kfk console-producer --topic my-topic -n kafka -c my-cluster --producer.config client.properties
```
The console producer seems to be working just fine since we can produce messages. 

```
>message1
>message2
>message3
>
```

Let's run the console consumer to consume the just produced messages:

```shell
kfk console-consumer --topic my-topic -n kafka -c my-cluster --consumer.config client.properties
```

```
message1
message2
message3
```

Worked like a charm!

We are able to configure the Strimzi cluster and use the client configurations for TLS authentication easily with Strimzi Kafka CLI.
