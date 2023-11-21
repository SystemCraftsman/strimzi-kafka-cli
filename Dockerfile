ARG KUBECONFIG=""
FROM python:3.11.6-alpine
USER root
RUN adduser -D kfkuser
RUN pip install strimzi-kafka-cli==0.1.0a74
USER kfkuser
RUN mkdir ~/.kube
RUN echo "${KUBECONFIG}" > /home/kfkuser/.kube/config
RUN kfk --version
