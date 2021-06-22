#Run this first if the cluster operator version is not compitable with the current Strimzi version
#export STRIMZI_KAFKA_CLI_STRIMZI_VERSION=0.22.1
kubectl create namespace kafka
kfk clusters --create --cluster my-cluster --replicas 2 --zk-replicas 1 -n kafka -y ;
kubectl create -f elasticsearch.yaml -n kafka ;
oc expose svc elasticsearch-es-http -n kafka ;
