FROM ubuntu:16.04
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV LANG='C.UTF-8' LC_ALL='C.UTF-8'
ENV DISTRIB_CODENAME=xenial DISTRIB_RELEASE=16.04
ENV CONFIG_DIR config

ENV FORCE_UPDATE 2

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends supervisor python python-dev python-pip python3-pip curl mc less \
    software-properties-common wget vim gcc unzip apt-utils net-tools cron netcat sudo file iproute2 bash-completion

RUN add-apt-repository -y ppa:vbernat/haproxy-1.8
RUN apt-get update
RUN apt-get install -y --no-install-recommends haproxy
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

RUN pip3 install -U pip setuptools
RUN pip2 install -U pip setuptools
RUN pip2 install -U web.py

RUN mkdir -p /var/log/supervisor /var/opt/service-registration/

COPY ./supervisor/* /etc/supervisor/conf.d/
COPY ./scripts/bash_completion/* /etc/bash_completion.d/
COPY . /opt/microservice
RUN ln -s /opt/microservice/microservice /opt/microservice/src

ENV MICROSERVICE_VERSION 2.4.3
RUN echo VERSION = \"${MICROSERVICE_VERSION}\" > /opt/microservice/microservice/version.py

RUN pip2 install -U /opt/microservice
RUN pip3 install -U /opt/microservice

RUN chmod +x /opt/microservice/scripts/* /opt/microservice/src/run_hooks.py
RUN /opt/microservice/scripts/install_tools.sh

RUN echo "\nsource /etc/bash_completion" >> /etc/bash.bashrc

CMD ["microservice", "bootstrap"]
