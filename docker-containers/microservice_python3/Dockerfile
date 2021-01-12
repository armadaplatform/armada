FROM docker.io/ubuntu:20.04
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV LANG='C.UTF-8' LC_ALL='C.UTF-8'
ENV DISTRIB_CODENAME=focal DISTRIB_RELEASE=20.04
ENV CONFIG_DIR config

ENV MICROSERVICE_VERSION 2.10.2

RUN apt-get update && apt-get upgrade -y

# Set up container's timezone
RUN DEBIAN_FRONTEND="noninteractive" TZ="Etc/UTC" apt-get install -y tzdata

#--- Install common utils ---
RUN apt-get install -y --no-install-recommends \
    supervisor git curl mc less software-properties-common wget vim gcc \
    unzip apt-utils net-tools cron netcat sudo file iproute2 bash-completion

#--- Install required Python version. ---
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.7 python3.7-dev
RUN rm /usr/bin/python3 && ln -s /usr/bin/python3.7 /usr/bin/python3
RUN sed -i 's@/usr/bin/python3@/usr/bin/python3.8@' /usr/bin/add-apt-repository

#--- Install corresponding pip version. ---
RUN cd /tmp && wget "https://bootstrap.pypa.io/get-pip.py" && sync && python3 get-pip.py && rm get-pip.py

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

CMD ["microservice", "bootstrap"]

RUN python3 -m pip install --upgrade setuptools
RUN python3 -m pip install --upgrade /opt/microservice

COPY ./src /opt/microservice_python3/src

ENV PYTHONPATH /opt/microservice_python3/src
