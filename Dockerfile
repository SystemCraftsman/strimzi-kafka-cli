FROM python:3.11.6-alpine
USER root
RUN adduser -D kfkuser
RUN pip install strimzi-kafka-cli==0.1.0a76
USER kfkuser
RUN mkdir /home/kfkuser/.kube
RUN curl https://raw.githubusercontent.com/SystemCraftsman/strimzi-kafka-cli/main/tests/files/yaml/kubeconfig -o /home/kfkuser/.kube/config
RUN kfk --version
