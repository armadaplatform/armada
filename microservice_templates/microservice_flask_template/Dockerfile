FROM microservice_flask
ENV IMAGE_NAME=example-rum-counter
MAINTAINER Cerebro <cerebro@ganymede.eu>


RUN pip3 install -U raven[flask]

ENV CONFIG_DIR config

ADD . /opt/$IMAGE_NAME
