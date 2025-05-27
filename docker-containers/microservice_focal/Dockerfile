FROM docker.io/ubuntu:20.04
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV LANG='C.UTF-8' LC_ALL='C.UTF-8'
ENV DISTRIB_CODENAME=focal DISTRIB_RELEASE=20.04
ENV CONFIG_DIR config

ENV MICROSERVICE_VERSION 2.13.1

# Set up container's timezone
RUN DEBIAN_FRONTEND="noninteractive" apt-get update && apt-get install -y tzdata

#--- Install common utils ---
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        apt-utils \
        bash-completion \
        cron \
        curl \
        file \
        gcc \
        git \
        iproute2 \
        less \
        mc \
        nano \
        net-tools \
        netcat \
        python3 \
        python3-dev \
        python3-pip \
        sudo \
        software-properties-common \
        supervisor \
        unzip \
        vim \
        wget \
        libffi-dev \
        build-essential

#--- Install haproxy ---
RUN add-apt-repository -y ppa:vbernat/haproxy-2.2
RUN apt-get update
RUN apt-get install -y --no-install-recommends haproxy

#--- Install armada ---
COPY ./armada-microservice_${MICROSERVICE_VERSION}_amd64.deb /tmp/armada-microservice_${MICROSERVICE_VERSION}_amd64.deb
RUN dpkg -i /tmp/armada-microservice_${MICROSERVICE_VERSION}_amd64.deb || true
RUN apt-get install -y --fix-broken --no-install-recommends
RUN dpkg -l armada-microservice

#--- Cleanup ---
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

#--- Add python alias ---
RUN ln -s /usr/bin/python3 /usr/bin/python

CMD ["microservice", "bootstrap"]
