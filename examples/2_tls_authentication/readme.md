# TLS Authentication with Strimzi using Strimzi Kafka CLI

In this example we will demonstrate setting up TLS authentication for Strimzi using Strimzi Kafka CLI. So let's get started!


First lets list the clusters and see our clusters list.

```shell
kfk clusters --list
```
    
Assuming we have a cluster already set up for us let's list the topics in the cluster

```shell
kfk topics --list -n kafka -c my-cluster
```
    
---
**NOTE**

If you don't have any Kafka cluster that is created on your OpenShift/Kubernetes, pls. see the [Strimzi Quick Start](https://strimzi.io/quickstarts/) document or simply use

```shell
kfk clusters --create -n kafka
```

---

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

Now lets enable the authentication for TLS. In Strimzi, if you want to
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
plain listener for authentication because with the upper configuration
if we don’t use a client configuration that doesn’t use SSL security
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

You got some WARN log messages saying
`disconnected (org.apache.kafka.clients.NetworkClient)` from both
producer and consumer right?

When we check the first pod logs that we ran the producer and consumer
commands we can see the failed authentication message:

```shell
oc logs -f my-cluster-kafka-0 -c kafka -n kafka
```

    2020-09-22 11:18:33,122 INFO [SocketServer brokerId=0] Failed authentication with /10.130.2.58 (Unexpected Kafka request of type METADATA during SASL handshake.) (org.apache.kafka.common.network.Selector) [data-plane-kafka-network-thread-0-ListenerName(PLAIN-9092)-SASL_PLAINTEXT-3]

Since we are not yet using SSL for authentication, but the PLAIN
connection method, which we set up as `scram-sha-512`, we can not
authenticate to the Strimzi Kafka cluster.

In order to login this cluster via SSL authentication we have to;

* Create a user that uses TLS authentication
* Create truststore and keystore files by getting the certificates from Openshift/Kubernetes cluster
* Create a client.properties file that is to be used by producer and consumer clients in order to be able to authenticate via TLS

