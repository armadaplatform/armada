FROM microservice_noble

LABEL maintainer="Cerebro <cerebro@ganymede.eu>"

# Install Python and dependencies in single layer
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-dev \
        python3-pip \
        python3-setuptools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY ./src /opt/microservice_python3/src/

# Install microservice package
RUN python3 -m pip install --no-cache-dir --upgrade /opt/microservice

# Set Python path
ENV PYTHONPATH="/opt/microservice_python3/src"