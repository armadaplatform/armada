FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV ARMADA_APT_GET_UPDATE_DATE 2016-12-29
RUN apt-get update && apt-get install -y rsync openssh-server libffi-dev libssl-dev python-dev
RUN pip install paramiko web.py docker-py==1.7.1 raven contextlib2 ujson

# Consul
RUN wget https://releases.hashicorp.com/consul/0.7.5/consul_0.7.5_linux_amd64.zip -O consul.zip
RUN unzip consul.zip && mv consul /usr/local/bin && rm -f consul.zip

ADD ./armada_backend/supervisor/* /etc/supervisor/conf.d/
RUN rm -f /etc/supervisor/conf.d/local_magellan.conf
ADD ./armada_backend/health-checks/* /opt/armada-docker/health-checks/

# armada
ADD . /opt/armada-docker
RUN ln -s /opt/armada-docker/microservice_templates /opt/templates
RUN cd /opt/armada-docker/armada_backend/scripts && chmod +x * && sync && ./setup_ssh.sh

ADD ./packaging/bin/armada /usr/local/bin/armada
RUN chmod +x /usr/local/bin/armada

ENV ARMADA_VERSION 1.16.0
RUN echo __version__ = \"armada ${ARMADA_VERSION}\" > /opt/armada-docker/armada_command/_version.py

ENV PYTHONPATH /opt/armada-docker:$PYTHONPATH

EXPOSE 22 80 8300 8301 8301/udp 8400 8500
