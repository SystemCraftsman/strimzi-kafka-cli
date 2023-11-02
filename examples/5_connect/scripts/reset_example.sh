#!/bin/bash
#Delete connect sources
kfk connect connectors --delete --connector twitter-source-demo -c my-connect-cluster -n kafka
kfk connect connectors --delete --connector camel-elasticsearch-sink-demo -c my-connect-cluster -n kafka
kfk connect clusters --delete --cluster my-connect-cluster -n kafka -y

#Delete topics
kfk topics --delete --topic twitter-status-connect -c my-cluster -n kafka
kfk topics --delete --topic twitter-deletes-connect -c my-cluster -n kafka

#Optional (Kafka Cluster & ElasticSearch deletion)
#kfk clusters --delete --cluster my-cluster -n kafka -y ;
#oc delete -f elasticsearch.yaml -n kafka
