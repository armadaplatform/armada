FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN curl -sL https://deb.nodesource.com/setup_0.12 | bash -
RUN apt-get install -y nodejs

ADD . /opt/microservice_node

ENV MICROSERVICE_NODE_PATH /opt/microservice_node/src
