FROM docker.io/ubuntu:20.04

RUN apt-get update && apt-get upgrade -y

# Set up container's timezone
RUN DEBIAN_FRONTEND="noninteractive" TZ="Etc/UTC" apt-get install -y tzdata

RUN apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        git \
        libc6-dev \
        make \
        python3 \
        rpm \
        xz-utils \
        tar \
        libarchive-tools \
        ruby-dev \
        libffi-dev

# install package builder
RUN gem install fpm

COPY build_armada.py /usr/bin/build_armada
RUN chmod +x /usr/bin/build_armada

WORKDIR "/opt/armada"
VOLUME "/opt/armada"
ENTRYPOINT ["/usr/bin/build_armada"]
