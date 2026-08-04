FROM python:3.12.2-alpine
USER root
RUN apk add --update \
    curl \
    && rm -rf /var/cache/apk/*
RUN adduser -D kfkuser
COPY dist/ /tmp/dist/
RUN pip install /tmp/dist/*.whl && rm -rf /tmp/dist/
USER kfkuser
RUN mkdir /home/kfkuser/.kube
COPY tests/files/yaml/kubeconfig /home/kfkuser/.kube/config
RUN kfk --version
