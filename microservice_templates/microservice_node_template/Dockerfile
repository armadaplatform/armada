FROM microservice_node
MAINTAINER Cerebro <cerebro@ganymede.eu>

ADD src/package.json /opt/package.json
RUN cd /opt && npm install --no-bin-links

# Uncomment following line to tell hermes, that you want to use configuration stored locally, in this case - in "config" subdirectory, relative to Dockerfile
# ENV CONFIG_DIR ./config

ADD . /opt/_MICROSERVICE_NODE_TEMPLATE_
ADD ./supervisor/_MICROSERVICE_NODE_TEMPLATE_.conf /etc/supervisor/conf.d/_MICROSERVICE_NODE_TEMPLATE_.conf

EXPOSE 80
