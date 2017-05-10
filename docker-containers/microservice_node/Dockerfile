FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN apt-get update
RUN curl -sL https://deb.nodesource.com/setup_0.12 | bash -
RUN apt-get install -y nodejs=0.12.18-1nodesource1~xenial1 make

RUN cd /tmp && wget https://github.com/npm/npm/archive/v2.15.11.tar.gz && tar -xf v2.15.11.tar.gz && cd npm-2.15.11 && make install

ADD . /opt/microservice_node

ENV MICROSERVICE_NODE_PATH /opt/microservice_node/src
