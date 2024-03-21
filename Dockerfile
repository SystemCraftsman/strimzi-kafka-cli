FROM python:3.12.2-alpine
USER root
RUN apk add --update \
    curl \
    && rm -rf /var/cache/apk/*
RUN adduser -D kfkuser
RUN pip install strimzi-kafka-cli==0.1.0a77
USER kfkuser
RUN mkdir /home/kfkuser/.kube
RUN curl https://raw.githubusercontent.com/SystemCraftsman/strimzi-kafka-cli/main/tests/files/yaml/kubeconfig -o /home/kfkuser/.kube/config
RUN kfk --version
