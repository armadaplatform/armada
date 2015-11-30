FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV MICROSERVICE_PYTHON3_5_APT_GET_UPDATE_DATE 2015-11-12
RUN sudo add-apt-repository ppa:fkrull/deadsnakes
RUN apt-get update
RUN apt-get install -y python3.5
RUN python3.5 /tmp/scripts/get-pip.py
RUN pip3.5 install -U requests

ADD . /opt/microservice_python3.5

ENV PYTHONPATH /opt/microservice_python3.5/src
