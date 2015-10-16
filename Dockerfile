FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV ARMADA_APT_GET_UPDATE_DATE 2015-07-17

RUN apt-get update
RUN apt-get install -y python python-dev unzip rsync
RUN pip install -U paramiko web.py docker-py==1.2.2

# Consul

RUN wget https://dl.bintray.com/mitchellh/consul/0.4.1_linux_amd64.zip -O consul.zip
RUN unzip consul.zip && mv consul /usr/local/bin && rm -f consul.zip

ADD ./armada_backend/supervisor/* /etc/supervisor/conf.d/
RUN rm -f /etc/supervisor/conf.d/local_magellan.conf
ADD ./armada_backend/health-checks/* /opt/armada-docker/health-checks/

# armada
ENV ARMADA_VERSION 0.8.0

ADD ./armada_command /opt/armada-docker/armada_command
RUN echo __version__ = \"armada ${ARMADA_VERSION}\" > /opt/armada-docker/armada_command/_version.py
ADD ./armada_backend /opt/armada-docker/armada_backend
ADD ./microservice_templates /opt/armada-docker/microservice_templates
ADD ./keys /opt/armada-docker/keys

ADD ./install/armada /usr/local/bin/armada
RUN chmod +x /usr/local/bin/armada

ENV PYTHONPATH /opt/armada-docker:$PYTHONPATH

EXPOSE 80 8300 8301 8301/udp 8400 8500
