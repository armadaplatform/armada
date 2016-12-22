FROM microservice_dotnet
MAINTAINER Adam Marszałek <sceeter89@outlook.com>


ADD . /opt/_MICROSERVICE_DOTNET_TEMPLATE_

RUN cd /opt/_MICROSERVICE_DOTNET_TEMPLATE_ && dotnet restore && dotnet build

ADD ./supervisor/_MICROSERVICE_DOTNET_TEMPLATE_.conf /etc/supervisor/conf.d/_MICROSERVICE_DOTNET_TEMPLATE_.conf

EXPOSE 80

