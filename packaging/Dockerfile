FROM ubuntu:16.04

RUN apt-get update && apt-get install -y --no-install-recommends \
		g++ \
		gcc \
		git \
		libc6-dev \
		make \
		python3 \
		rpm \
		ruby-dev

# install package builder
RUN gem install fpm

COPY build_armada.py /usr/bin/build_armada
RUN chmod +x /usr/bin/build_armada

WORKDIR "/opt/armada"
VOLUME "/opt/armada"
ENTRYPOINT ["/usr/bin/build_armada"]
