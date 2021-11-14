#!/bin/bash
#Run this first if the cluster operator version is not compitable with the current Strimzi version
#export STRIMZI_KAFKA_CLI_STRIMZI_VERSION=0.22.1
kfk clusters --create --cluster my-cluster --replicas 2 --zk-replicas 1 -n kafka -y
oc create -f ../elasticsearch.yaml -n kafka
oc expose svc elasticsearch-es-http -n kafka
