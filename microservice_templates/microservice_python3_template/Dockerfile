FROM microservice_python3
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN pip3 install -U bottle

# Uncomment following line to tell hermes, that you want to use configuration stored locally, in this case - in "config" subdirectory, relative to Dockerfile
# ENV CONFIG_DIR ./config

ADD . /opt/_MICROSERVICE_PYTHON3_TEMPLATE_
ADD ./supervisor/_MICROSERVICE_PYTHON3_TEMPLATE_.conf /etc/supervisor/conf.d/_MICROSERVICE_PYTHON3_TEMPLATE_.conf

EXPOSE 80
