FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV ARMADA_APT_GET_UPDATE_DATE 2016-08-03
RUN apt-get update && apt-get install -y python python-dev python-pip unzip rsync openssh-server libffi-dev libssl-dev
RUN pip install paramiko web.py docker-py==1.7.1 raven contextlib2

# Consul
RUN wget https://releases.hashicorp.com/consul/0.6.4/consul_0.6.4_linux_amd64.zip -O consul.zip
RUN unzip consul.zip && mv consul /usr/local/bin && rm -f consul.zip

ADD ./armada_backend/supervisor/* /etc/supervisor/conf.d/
RUN rm -f /etc/supervisor/conf.d/local_magellan.conf
ADD ./armada_backend/health-checks/* /opt/armada-docker/health-checks/

# armada
ADD . /opt/armada-docker
RUN ln -s /opt/armada-docker/microservice_templates /opt/templates
RUN cd /opt/armada-docker/armada_backend/scripts && chmod +x * && sync && ./setup_ssh.sh

ADD ./install/armada /usr/local/bin/armada
RUN chmod +x /usr/local/bin/armada

ENV ARMADA_VERSION 1.8.1
RUN echo __version__ = \"armada ${ARMADA_VERSION}\" > /opt/armada-docker/armada_command/_version.py

ENV PYTHONPATH /opt/armada-docker:$PYTHONPATH

EXPOSE 22 80 8300 8301 8301/udp 8400 8500
