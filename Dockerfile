FROM python:3-alpine
RUN adduser -D kfkuser
USER root
RUN pip install strimzi-kafka-cli==0.1.0a15
USER kfkuser
RUN kfk