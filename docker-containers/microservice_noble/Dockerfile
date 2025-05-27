FROM docker.io/ubuntu:24.04

LABEL maintainer="Cerebro <cerebro@ganymede.eu>"

# Environment variables
ENV MICROSERVICE_VERSION 2.13.1
ENV LANG='C.UTF-8' \
    LC_ALL='C.UTF-8' \
    DISTRIB_CODENAME=noble \
    DISTRIB_RELEASE=24.04 \
    CONFIG_DIR=config \
    DEBIAN_FRONTEND=noninteractive

# Install all packages in single layer
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        # System essentials
        apt-utils \
        tzdata \
        # Development tools
        build-essential \
        gcc \
        libffi-dev \
        libpcre3-dev \
        libssl-dev \
        zlib1g-dev \
        # Python
        python3 \
        python3-dev \
        python3-pip \
        # Network and system tools
        curl \
        wget \
        net-tools \
        netcat-openbsd \
        iproute2 \
        # Text editors and utilities
        bash-completion \
        file \
        less \
        mc \
        nano \
        vim \
        # Version control and package management
        git \
        software-properties-common \
        unzip \
        # System services
        cron \
        supervisor \
        sudo \
        # HAProxy dependencies
        lua5.3 \
        liblua5.3-dev \
        haproxy \
    # Cleanup in same layer
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Remove Python externally-managed restriction
    && find /usr/lib/ -type f -name 'EXTERNALLY-MANAGED' -delete \
    # Create Python alias
    && ln -sf /usr/bin/python3 /usr/bin/python

# Verify HAProxy installation
RUN haproxy -v

# Install armada microservice
ARG MICROSERVICE_VERSION=2.11.43
COPY ./armada-microservice_${MICROSERVICE_VERSION}_amd64.deb /tmp/
RUN dpkg -i /tmp/armada-microservice_${MICROSERVICE_VERSION}_amd64.deb || true \
    && apt-get update \
    && apt-get install -y --fix-broken --no-install-recommends \
    && dpkg -l armada-microservice \
    && rm -f /tmp/armada-microservice_${MICROSERVICE_VERSION}_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

CMD ["microservice", "bootstrap"]