FROM python:3.11.6-alpine
USER root
RUN adduser -D kfkuser
RUN pip install strimzi-kafka-cli==0.1.0a73
USER kfkuser
RUN mkdir ~/.kube
COPY ~/.kube/config /home/kfkuser/.kube/config
RUN kfk --version
