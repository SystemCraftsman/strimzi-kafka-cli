# Simple ACL Authorization on Strimzi by using Strimzi Kafka CLI

```shell
kfk clusters --list
```

```shell
kfk topics --list -n kafka -c my-cluster
```

```shell
kfk users --list -n kafka -c my-cluster
```

```shell
kfk clusters --alter --cluster my-cluster -n kafka
```

```yaml
authorization:
  type: simple
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

```shell
kfk console-consumer --topic my-topic -n kafka -c my-cluster --consumer.config client.properties
```

```shell
kfk acls --add --allow-principal User:my-user --group my-group --operation Read -n kafka -c my-cluster
```

```shell
kfk console-producer --topic my-topic -n kafka -c my-cluster --producer.config client.properties
```

```shell
kfk console-consumer --topic my-topic -n kafka -c my-cluster --consumer.config client.properties
```
