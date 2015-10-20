FROM ubuntu:14.04
MAINTAINER Cerebro <cerebro@ganymede.eu>

# You can force apt-get update & upgrade on next 'armada build' by changing the date:
ENV MICROSERVICE_FORCE_APT_GET_UPDATE 2015-10-19

ADD scripts/install_packages.sh /tmp/scripts/
# 'sync' is to fix "text file busy" error.
RUN cd /tmp/scripts && chmod +x * && sync && ./install_packages.sh
ADD . /opt/microservice
RUN cd /opt/microservice/scripts && chmod +x * && sync && ./setup_ssh.sh && ./setup_supervisor.sh
RUN mkdir /var/opt/service-registration/

EXPOSE 22

CMD ["/usr/bin/python3.4", "/opt/microservice/src/bootstrap_microservice.py"]
