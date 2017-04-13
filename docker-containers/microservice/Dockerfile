FROM ubuntu:16.04
MAINTAINER Cerebro <cerebro@ganymede.eu>

# You can force apt-get update & upgrade on next 'armada build' by changing the date:
ENV MICROSERVICE_APT_GET_UPDATE_DATE 2016-12-29

ENV LANG='C.UTF-8' LC_ALL='C.UTF-8' DEBIAN_FRONTEND='noninteractive'

# 'sync' is to fix "text file busy" error.
ADD . /opt/microservice
RUN cd /opt/microservice/scripts && chmod +x * && sync && ./install_packages.sh && ./setup_supervisor.sh
RUN mkdir /var/opt/service-registration/

CMD ["/usr/bin/python3", "/opt/microservice/src/bootstrap_microservice.py"]
