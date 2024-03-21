FROM python:3.11.6-alpine
ARG KUBECONFIG
USER root
RUN adduser -D kfkuser
RUN pip install strimzi-kafka-cli==0.1.0a75
USER kfkuser
RUN mkdir /home/kfkuser/.kube
RUN echo "$KUBECONFIG" > /home/kfkuser/.kube/config
RUN kfk --version
