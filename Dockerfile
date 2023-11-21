FROM python:3.11.6-alpine
USER root
RUN adduser -D kfkuser
RUN pip install strimzi-kafka-cli==0.1.0a72
USER kfkuser
RUN kfk --version
