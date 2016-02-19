FROM microservice

RUN apt-get update && apt-get install -y --no-install-recommends \
		g++ \
		gcc \
		git \
		libc6-dev \
		make \
	&& rm -rf /var/lib/apt/lists/*

ENV GOLANG_VERSION 1.5.3
ENV GOLANG_DOWNLOAD_URL https://golang.org/dl/go$GOLANG_VERSION.linux-amd64.tar.gz
ENV GOLANG_DOWNLOAD_SHA256 43afe0c5017e502630b1aea4d44b8a7f059bf60d7f29dfd58db454d4e4e0ae53

RUN curl -fsSL "$GOLANG_DOWNLOAD_URL" -o golang.tar.gz \
	&& echo "$GOLANG_DOWNLOAD_SHA256  golang.tar.gz" | sha256sum -c - \
	&& tar -C /usr/local -xzf golang.tar.gz \
	&& rm golang.tar.gz

ENV GOPATH /go
RUN ln -s /usr/local/go/bin/go /usr/local/bin/
RUN ln -s /usr/local/go/bin/godoc /usr/local/bin/
RUN ln -s /usr/local/go/bin/gofmt /usr/local/bin/

RUN mkdir -p "$GOPATH/src" "$GOPATH/bin"

RUN go get github.com/tools/godep
RUN ln -s "$GOPATH/bin/godep" /usr/local/bin/

RUN go get github.com/tools/godep

