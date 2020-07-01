FROM python:3-slim-buster
RUN adduser -D kfkuser
USER root
RUN pip install strimzi-kafka-cli==0.1.0a20
USER kfkuser
RUN kfk version