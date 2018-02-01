FROM ubuntu:16.04
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV LANG='C.UTF-8' LC_ALL='C.UTF-8'
ENV DISTRIB_CODENAME=xenial DISTRIB_RELEASE=16.04
ENV CONFIG_DIR config

ENV MICROSERVICE_VERSION 2.4.3

ENV FORCE_UPDATE 2

RUN apt-get update
RUN apt-get upgrade -y

COPY ./armada-microservice_${MICROSERVICE_VERSION}_amd64.deb /tmp
RUN dpkg -i /tmp/armada-microservice_${MICROSERVICE_VERSION}_amd64.deb
RUN apt-get install -f -y

RUN add-apt-repository -y ppa:vbernat/haproxy-1.8
RUN apt-get update
RUN apt-get install -y --no-install-recommends haproxy
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

RUN echo VERSION = \"${MICROSERVICE_VERSION}\" > /opt/microservice/microservice/version.py

CMD ["microservice", "bootstrap"]
