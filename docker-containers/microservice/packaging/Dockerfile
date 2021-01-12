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
        ruby-dev \
        ruby \
        rubygems \
        build-essential \
        libffi-dev

# Install package builder
RUN gem install fpm

COPY package_build.py /usr/bin/package_build
RUN chmod +x /usr/bin/package_build

WORKDIR "/opt/microservice"
VOLUME "/opt/microservice"
ENTRYPOINT ["/usr/bin/package_build"]
