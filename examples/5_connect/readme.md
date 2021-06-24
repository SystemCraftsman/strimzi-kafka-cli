# Kafka Connect

In this example, we will create a Kafka Connect cluster, and a few connectors that consumes particular twitter topics and writes them to an elasticsearch index to be searched easily.

We are not going to deal with any custom resources of Strimzi.
Instead we will use traditional `.property` files that are used for Kafka Connect instances and connectors, with the help of Strimzi Kafka CLI.

## Prerequisites

* A Kubernetes/OpenShift cluster that has Strimzi Kafka Operator installed.
* A namespace called `kafka` and a Kafka cluster called `my-cluster`
* An elasticsearch instance up and running in the same  namespace.
* A public image registry that has a repository called `demo-connect-cluster`.
* Most importantly, a `Twitter Developer Account` that enables you to use Twitter API for development purposes.
In this example we are going to use it with one of our Kafka Connect connectors.

As a recommendation create the namespace first:

```shell
oc new-project kafka
```

Then install the Strimzi Operator if its not installed.
You can use Strimzi CLI for this:

```shell
kfk operator --install -n kafka
```

Create Kafka and Elasticsearch cluster by running the `setup_example.sh` script:

```shell
chmod +x ./scripts/setup_example.sh
./scripts/setup_example.sh
```

This will create a Kafka cluster with 2 brokers, and an Elasticsearch cluster that's accessible through a Route.

---
**NOTE**

If you are using Kubernetes you can create an Ingress and expose the Elasticsearch instance.

Exposing the Elasticsearch instance is not mandatory.

---

Lastly create an empty repository in any image registry of your choice.
For this example we are going to use Quay.io as our repository will be `quay.io/systemcraftsman/demo-connect-cluster`.

## Creating a Kafka Connect Cluster

For this example, to show how it is easy to create a Kafka Connect cluster with a traditional properties file, we will use an example of a well-known Kafka instructor, Stephane Maarek, who demonstrates a very basic Twitter Source Connector in one of his courses.

So let's clone the repository `https://github.com/simplesteph/kafka-beginners-course.git` and change directory into the `kafka-connect` folder in the repository.

In the repository we have this `connect-standalone.properties` file which has the following config in it:

```properties
...Output omitted...
bootstrap.servers=localhost:9092

...Output omitted...
key.converter.schemas.enable=true
value.converter.schemas.enable=true

offset.storage.file.filename=/tmp/connect.offsets
# Flush much faster than normal, which is useful for testing/debugging
offset.flush.interval.ms=10000

...Output omitted...
plugin.path=connectors
```

Kafka Connect normally has this `plugin.path` key which has the all connector binaries to be used for any connector created for that Connect cluster.
In our case, for Strimzi, it will be a bit different because we are going to create our connect cluster in a Kubernetes/OpenShift environment, so we should either create an image locally, or make Strimzi create the connect image for us.
We will use the second option, which is fairly a new feature of Strimzi.

Only thing we have to do, instead of defining a path, we will define a set of url that has the different connector resources.
So let's copy the file that Stephane created for us and save it as `connect.properties` since Kafka Connect works in the distributed mode in Strimzi (there is no standalone mode in short).

In the `connect.properties` file change the `plugin.path` with `plugin.url` and set the following source url to it:

```properties
plugin.url=https://github.com/jcustenborder/kafka-connect-twitter/releases/download/0.2.26/kafka-connect-twitter-0.2.26.tar.gz
```

By comparing to the original repository, you can see in the `connectors` folder there are a bunch of jar files that Twitter Source Connector uses.
The url that you set above has the same resources archived.
Strimzi extracts them while building the Connect image in the Kubernetes/OpenShift cluster.

Speaking of the image, we have to set a `output.image`, actually a image repository path, that Strimzi can push the built image into.
This can be either an internal registry of yours, or a public one like Docker Hub or Quay.
In this example we will use Quay and we should set the image URL like the following:

```properties
output.image=quay.io/systemcraftsman/demo-connect-cluster:latest
```

Here you can set the repository URL of your choice instead of `quay.io/systemcraftsman/demo-connect-cluster:latest`.
As a prerequisite, you have to create this repository and make the credentials ready for the image push for Strimzi.

Apart from the `plugin.path`, we can do a few changes like changing the offset storage to a topic instead of a file and disabling the key/value converter schemas because we will just barely need to see the data itself; we don't need the JSON schemas.

So the final connector.properties file should look like this:

```properties
...Output omitted...

bootstrap.servers=my-cluster-kafka-bootstrap:9092

# The converters specify the format of data in Kafka and how to translate it into Connect data. Every Connect user will
# need to configure these based on the format they want their data in when loaded from or stored into Kafka
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
# Converter-specific settings can be passed in by prefixing the Converter's setting with the converter we want to apply
# it to
key.converter.schemas.enable=false
value.converter.schemas.enable=false

offset.storage.topic=connect-cluster-offsets
config.storage.topic=connect-cluster-configs
status.storage.topic=connect-cluster-status
config.storage.replication.factor=1
offset.storage.replication.factor=1
status.storage.replication.factor=1

...Output omitted...

output.image=quay.io/systemcraftsman/demo-connect-cluster:latest
plugin.url=https://github.com/jcustenborder/kafka-connect-twitter/releases/download/0.2.26/kafka-connect-twitter-0.2.26.tar.gz
```

```shell
kfk connect clusters --create --cluster my-connect-cluster --replicas 1 -n kafka connect.properties twitter_connector.properties -u _YOUR_IMAGE_REGISTRY_USER_ -y
```

Replace your image registry user with `_YOUR_IMAGE_REGISTRY_USER_` and run the command.

You should be asked for the registry password.
Enter the password and observe the CLI response as follows:

```
TODO:
```

---
**IMPORTANT**

Be careful while entering that because there is no mechanism that checks this password in Strimzi Kafka CLI, so if the password is wrong, simply the Connect image will be built sucessfully, but Strimzi won't be able to push it to the registry you specified before.

In case of any problem just delete the Connect cluster with the following command and create it again:

```shell
kfk connect clusters --delete --cluster my-connect-cluster -n kafka -y
````

Or you can delete/create the push secret that is created if you are familiar enough.

---

---
**IMPORTANT**

You can also create the cluster with a more controlled way; by not passing the `-y` flag.
Without the `-y` flag, Strimzi Kafka CLI shows you the resource YAML of the Kafka Connect cluster in an editor, and you can modify or just save the resource before the creation.
In this example we skip this part with `-y` flag.

---

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

## Creating a Twitter Source Connector

```shell
kfk topics --create --topic twitter-status-connect --partitions 3 --replication-factor 1 -c my-cluster -n kafka
```

```shell
kfk topics --create --topic twitter-deletes-connect --partitions 3 --replication-factor 1 -c my-cluster -n kafka
```


<!--- 
Show them the tweet stream by consuming the twitter-status-connect topic
-->
```shell
kfk console-consumer --topic twitter-status-connect -c my-cluster -n kafka
```

## Altering the Connect Cluster

<!--- 
Alter the connect cluster to add another connector resource. this will be camel elasticsearch connector
-->
```shell
kfk connect clusters --alter --cluster my-connect-cluster -n kafka connect_v2.properties
```

<!--- 
Show the connector is being built again
-->
```shell
watch kubectl get pods -n kafka
```

## Creating a Camel Elasticsearch REST Sink Connector

<!--- 
Add another connector with kfk connect connector
-->
```shell
kfk connect connectors --create -c my-connect-cluster -n kafka camel_es_connector.properties
```

```shell
watch "curl -s http://_ELASTIC_EXTERNAL_URL_/tweets/_search | jq -r '.hits.total.value'"
```

<!--- 
Open elasticsearch and show them some newly indexed tweets and search for some
-->
```shell
curl -s http://_ELASTIC_EXTERNAL_URL_/tweets/_search?q=Text:Apache
```

## Deleting Connectors

```shell
kfk connect connectors --delete --connector twitter-source-demo -c my-connect-cluster -n kafka ;
kfk connect connectors --delete --connector camel-elasticsearch-sink-demo -c my-connect-cluster -n kafka ;
```

## Deleting Connect Cluster

```shell
kfk connect clusters --delete --cluster my-connect-cluster -n kafka -y
```