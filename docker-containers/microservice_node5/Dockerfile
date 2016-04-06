FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN curl -sL https://deb.nodesource.com/setup_5.x | bash -
RUN apt-get install -y nodejs

ADD . /opt/microservice_node5

ENV MICROSERVICE_NODE_PATH /opt/microservice_node5/src
