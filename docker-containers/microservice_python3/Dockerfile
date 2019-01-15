FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.7 python3.7-dev build-essential gcc
RUN rm /usr/bin/python3 && ln -s /usr/bin/python3.7 /usr/bin/python3
RUN cd /tmp && wget https://bootstrap.pypa.io/get-pip.py && sync && python3 get-pip.py && rm get-pip.py
RUN pip3 install -U setuptools
RUN pip3 install -U /opt/microservice
#pin python to version 3.5
RUN sed -i 's@/usr/bin/python3@/usr/bin/python3.5@' /usr/bin/add-apt-repository

ADD . /opt/microservice_python3

ENV PYTHONPATH /opt/microservice_python3/src
