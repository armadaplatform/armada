FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>
ARG NODE_VERSION=4
ENV MICROSERVICE_PATH="/opt/microservice_node${NODE_VERSION}"

RUN curl -sL "https://deb.nodesource.com/setup_${NODE_VERSION}.x" | bash -
RUN apt-get install -y nodejs

#hack for customizing node options by changing environmental variable
RUN mv $(readlink -e $(command -v nodejs)) /usr/bin/nodejs_bin
RUN rm -f /usr/bin/nodejs /usr/bin/node
COPY ./src/nodejs.sh /usr/bin/nodejs
RUN chmod +x /usr/bin/nodejs && ln -s /usr/bin/nodejs /usr/bin/node
#end hack

RUN mkdir ${MICROSERVICE_PATH}
ADD . ${MICROSERVICE_PATH}

ENV MICROSERVICE_NODE_PATH "${MICROSERVICE_PATH}/src"
