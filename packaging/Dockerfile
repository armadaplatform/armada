FROM microservice

RUN apt-get update && apt-get install -y --no-install-recommends \
		g++ \
		gcc \
		git \
		libc6-dev \
		make \
		rpm \
		ruby-dev \
	&& rm -rf /var/lib/apt/lists/*

# install package builder
RUN gem install fpm

WORKDIR "/opt/armada"
VOLUME "/opt/armada"

EXPOSE 80
