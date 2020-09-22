#!/usr/bin/env bash

rm truststore.jks user.p12

oc extract secret/my-user --keys=user.crt --to=- > user.crt
oc extract secret/my-user --keys=user.key --to=- > user.key
oc extract secret/my-cluster-cluster-ca-cert --keys=ca.crt --to=- > ca.crt

echo "yes" | keytool -import -trustcacerts -file ca.crt -keystore truststore.jks -storepass 123456
RANDFILE=/tmp/.rnd openssl pkcs12 -export -in user.crt -inkey user.key -name my-user -password pass:123456 -out user.p12

rm user.crt user.key ca.crt