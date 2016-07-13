FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN pip install -U armada

ADD . /opt/microservice_python

ENV PYTHONPATH /opt/microservice_python/src
