FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV MICROSERVICE_PYTHON3_5_APT_GET_UPDATE_DATE 2016-07-07
RUN sudo add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.5 wget
RUN cd /tmp && wget https://bootstrap.pypa.io/get-pip.py && sync && python3.5 get-pip.py
RUN pip3.5 install -U /opt/microservice

ADD . /opt/microservice_python3.5

ENV PYTHONPATH /opt/microservice_python3.5/src

RUN echo 'echo "WARNING: Base image microservice_python3.5 has been deprecated. Use microservice_python3 instead."' >> /etc/bash.bashrc
