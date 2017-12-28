FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update
RUN apt-get install -y python3.6 python3.6-dev build-essential gcc
RUN rm /usr/bin/python3 && ln -s /usr/bin/python3.6 /usr/bin/python3
RUN cd /tmp && wget https://bootstrap.pypa.io/get-pip.py && sync && python3 get-pip.py && rm get-pip.py
RUN pip3 install -U requests armada setuptools
RUN pip3 install -U 'http://dev.git.gd/filip_wojciak/armada-microservice/repository/archive.zip?ref=master'
#pin python to version 3.5
RUN sed -i 's@/usr/bin/python3@/usr/bin/python3.5@' /usr/bin/add-apt-repository

ADD . /opt/microservice_python3

ENV PYTHONPATH /opt/microservice_python3/src
