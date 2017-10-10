FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN curl -sL https://deb.nodesource.com/setup_5.x | bash -
RUN apt-get install -y nodejs

#hack for customizing node options by changing environmental variable
RUN mv /usr/bin/nodejs /usr/bin/nodejs_bin
COPY ./src/nodejs.sh /usr/bin/nodejs
RUN chmod +x /usr/bin/nodejs
#end hack

ADD . /opt/microservice_node5

ENV MICROSERVICE_NODE_PATH /opt/microservice_node5/src
