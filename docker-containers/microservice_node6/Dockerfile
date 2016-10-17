FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN apt-get install -y nodejs

ADD . /opt/microservice_node6

ENV MICROSERVICE_NODE_PATH /opt/microservice_node6/src
