FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN apt-get update && apt-get install -y rsync openssh-server libffi-dev libssl-dev python3-dev
RUN pip3 install -U paramiko 'docker==2.4.2' raven contextlib2 ujson colored armada-heal six falcon uwsgi \
    falcon_json_middleware requests

# Consul
RUN curl -s https://releases.hashicorp.com/consul/0.7.5/consul_0.7.5_linux_amd64.zip | zcat > /usr/local/bin/consul \
    && chmod +x /usr/local/bin/consul

ADD ./armada_backend/supervisor/* /etc/supervisor/conf.d/
RUN rm -f /etc/supervisor/conf.d/local_magellan.conf

# armada
ADD . /opt/armada-docker
RUN /opt/armada-docker/armada_backend/scripts/setup_ssh.sh
RUN ln -s /opt/armada-docker/microservice_templates /opt/templates
RUN ln -s /opt/armada-docker/packaging/bin/armada /usr/local/bin/armada

ENV ARMADA_VERSION 2.4.3
RUN echo __version__ = \"armada ${ARMADA_VERSION}\" > /opt/armada-docker/armada_command/_version.py

ENV PYTHONPATH /opt/armada-docker:$PYTHONPATH

EXPOSE 22 80 8300 8301 8301/udp 8400 8500
