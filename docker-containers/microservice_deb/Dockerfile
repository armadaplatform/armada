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

COPY build_microservice.py /usr/bin/microservice_build
RUN chmod +x /usr/bin/microservice_build

WORKDIR "/opt/microservice"
VOLUME "/opt/microservice"
ENTRYPOINT ["/usr/bin/microservice_build"]
