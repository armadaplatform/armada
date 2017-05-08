FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN    sh -c 'echo "deb [arch=amd64] http://apt-mo.trafficmanager.net/repos/dotnet-release/ xenial main" > /etc/apt/sources.list.d/dotnetdev.list' \
    && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 417A0893 \
    && apt-get update \
    && apt-get install -y dotnet-dev-1.0.0-preview2-003156 
