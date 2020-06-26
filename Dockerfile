FROM python:3-alpine
RUN adduser -D kfkuser
USER root
RUN pip install strimzi-kafka-cli
USER kfkuser
RUN kfk