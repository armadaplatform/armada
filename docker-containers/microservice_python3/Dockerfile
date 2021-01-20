FROM microservice_focal
MAINTAINER Cerebro <cerebro@ganymede.eu>

#--- Install required Python version. ---
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.7 python3.7-dev
RUN rm /usr/bin/python3 && ln -s /usr/bin/python3.7 /usr/bin/python3

#--- Pin python to version 3.8
RUN sed -i 's@/usr/bin/python3@/usr/bin/python3.8@' /usr/bin/add-apt-repository

#--- Install corresponding pip version. ---
RUN cd /tmp && wget "https://bootstrap.pypa.io/get-pip.py" && sync && python3 get-pip.py && rm get-pip.py

RUN python3 -m pip install --upgrade setuptools
RUN python3 -m pip install --upgrade /opt/microservice

COPY ./src /opt/microservice_python3/src

ENV PYTHONPATH /opt/microservice_python3/src
