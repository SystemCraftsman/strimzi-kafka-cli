FROM python:3.11.6-alpine
ARG KUBECONFIG
USER root
RUN adduser -D kfkuser
RUN pip install strimzi-kafka-cli==0.1.0a74
USER kfkuser
RUN mkdir ~/.kube
RUN echo "$KUBECONFIG" > ~/.kube/config
RUN kfk --version
