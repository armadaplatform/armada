FROM microservice_python3_focal
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN apt-get update && apt-get upgrade -y && apt-get install -y rsync openssh-server libffi-dev libssl-dev

COPY armada_backend/armada_backend_requirements.txt /tmp

RUN python3 -m pip install -r /tmp/armada_backend_requirements.txt

# Consul
RUN curl -s https://releases.hashicorp.com/consul/0.7.5/consul_0.7.5_linux_amd64.zip | zcat > /usr/local/bin/consul \
    && chmod +x /usr/local/bin/consul

COPY ./armada_backend/supervisor/* /etc/supervisor/conf.d/
RUN rm -f /etc/supervisor/conf.d/local_magellan.conf

# armada
COPY . /opt/armada-docker
RUN chmod a+rx /opt/armada-docker/armada_backend/scripts/setup_ssh.sh
RUN /opt/armada-docker/armada_backend/scripts/setup_ssh.sh
RUN ln -s /opt/armada-docker/microservice_templates /opt/templates
RUN ln -s /opt/armada-docker/packaging/bin/armada /usr/local/bin/armada

ENV ARMADA_VERSION 2.11.6
RUN echo __version__ = \"armada ${ARMADA_VERSION}\" > /opt/armada-docker/armada_command/_version.py

ENV PYTHONPATH /opt/armada-docker:$PYTHONPATH

EXPOSE 22 80 8300 8301 8301/udp 8400 8500
