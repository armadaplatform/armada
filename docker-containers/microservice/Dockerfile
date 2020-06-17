FROM docker.io/ubuntu:16.04
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV LANG='C.UTF-8' LC_ALL='C.UTF-8'
ENV DISTRIB_CODENAME=xenial DISTRIB_RELEASE=16.04
ENV CONFIG_DIR config

ENV MICROSERVICE_VERSION 2.10.1

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends supervisor python python-dev python-pip python3-pip curl mc less \
    software-properties-common wget vim gcc unzip apt-utils net-tools cron netcat sudo file iproute2 bash-completion

RUN add-apt-repository -y ppa:vbernat/haproxy-1.8
RUN apt-get update
RUN apt-get install -y --no-install-recommends haproxy

COPY ./armada-microservice_${MICROSERVICE_VERSION}_amd64.deb /tmp/armada-microservice_${MICROSERVICE_VERSION}_amd64.deb
RUN dpkg -i /tmp/armada-microservice_${MICROSERVICE_VERSION}_amd64.deb || true
RUN apt-get install -f -y --no-install-recommends
RUN dpkg -l armada-microservice

RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

CMD ["microservice", "bootstrap"]
