FROM python:3.11.6-alpine
ARG KUBECONFIG_CONTENT
ENV KUBECONFIG_CONTENT ${KUBECONFIG_CONTENT}
USER root
RUN adduser -D kfkuser
RUN pip install strimzi-kafka-cli==0.1.0a76
USER kfkuser
RUN mkdir /home/kfkuser/.kube
RUN echo "$KUBECONFIG_CONTENT" > /home/kfkuser/.kube/config
RUN kfk --version
