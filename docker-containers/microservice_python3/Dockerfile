FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN apt-get install -y python3 python3-dev python3-pip build-essential

RUN pip3 install -U pip
RUN pip3 install -U requests

ADD . /opt/microservice_python3

ENV PYTHONPATH /opt/microservice_python3/src
