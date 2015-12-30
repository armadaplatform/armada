FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV MICROSERVICE_PYTHON3_5_APT_GET_UPDATE_DATE 2015-12-28
RUN sudo add-apt-repository ppa:fkrull/deadsnakes
RUN apt-get update
RUN apt-get install -y python3.5 wget
RUN cd /tmp && wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py && sync && python3.5 get-pip.py
RUN pip3.5 install -U requests

ADD . /opt/microservice_python3.5

ENV PYTHONPATH /opt/microservice_python3.5/src
