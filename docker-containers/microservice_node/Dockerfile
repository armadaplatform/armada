FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN apt-get install -y nodejs
RUN apt-get install -y npm
RUN ln -s /usr/bin/nodejs /usr/bin/node

ADD . /opt/microservice_node

ENV MICROSERVICE_NODE_PATH /opt/microservice_node/src 
