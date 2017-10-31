FROM ubuntu:16.04
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV LANG='C.UTF-8' LC_ALL='C.UTF-8'
ENV DISTRIB_CODENAME=xenial DISTRIB_RELEASE=16.04

ENV CONFIG_DIR config

ADD . /opt/microservice
# 'sync' is to fix "text file busy" error.
RUN chmod +x /opt/microservice/src/run_hooks.py && \
    cd /opt/microservice/scripts && chmod +x * && sync && ./install_packages.sh && ./setup_supervisor.sh
RUN mkdir /var/opt/service-registration/
RUN ln -s /opt/microservice/scripts/alogs /usr/local/bin/alogs

RUN cp /opt/microservice/scripts/bash_completion/* /etc/bash_completion.d/
RUN echo "\nsource /etc/bash_completion" >> /etc/bash.bashrc

CMD ["/usr/bin/python3", "/opt/microservice/src/bootstrap_microservice.py"]
