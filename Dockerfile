FROM microservice_python3_noble

LABEL maintainer="Cerebro <cerebro@ganymede.eu>"

# Install system dependencies in single layer
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        rsync \
        openssh-server \
        libffi-dev \
        libssl-dev \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY armada_backend/armada_backend_requirements.txt /tmp/
RUN python3 -m pip install --no-cache-dir -r /tmp/armada_backend_requirements.txt \
    && rm /tmp/armada_backend_requirements.txt

# Install Consul
ARG CONSUL_VERSION=0.7.5
RUN curl -fsSL "https://releases.hashicorp.com/consul/${CONSUL_VERSION}/consul_${CONSUL_VERSION}_linux_amd64.zip" \
    | zcat > /usr/local/bin/consul \
    && chmod +x /usr/local/bin/consul

# Configure supervisor
COPY ./armada_backend/supervisor/* /etc/supervisor/conf.d/
RUN rm -f /etc/supervisor/conf.d/local_magellan.conf

# Copy and setup armada
COPY . /opt/armada-docker/

# Setup SSH and create symlinks
RUN chmod +x /opt/armada-docker/armada_backend/scripts/setup_ssh.sh \
    && /opt/armada-docker/armada_backend/scripts/setup_ssh.sh \
    && ln -sf /opt/armada-docker/microservice_templates /opt/templates \
    && ln -sf /opt/armada-docker/packaging/bin/armada /usr/local/bin/armada

# Set version
ARG ARMADA_VERSION=2.11.43
ENV ARMADA_VERSION=${ARMADA_VERSION}
RUN echo "__version__ = \"armada ${ARMADA_VERSION}\"" > /opt/armada-docker/armada_command/_version.py

# Set Python path
ENV PYTHONPATH="/opt/armada-docker:${PYTHONPATH}"

# Expose ports
EXPOSE 22 80 8300 8301 8301/udp 8400 8500