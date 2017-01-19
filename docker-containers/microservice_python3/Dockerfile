FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN add-apt-repository ppa:jonathonf/python-3.6
RUN add-apt-repository ppa:ubuntu-toolchain-r/test
RUN apt-get update
RUN apt-get install -y python3.6 python3.6-dev build-essential gcc-4.9 g++-4.9
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.9 60 --slave /usr/bin/g++ g++ /usr/bin/g++-4.9
RUN rm /usr/bin/x86_64-linux-gnu-gcc && ln -s /usr/bin/x86_64-linux-gnu-gcc-4.9 /usr/bin/x86_64-linux-gnu-gcc
RUN rm /usr/bin/python3 && ln -s /usr/bin/python3.6 /usr/bin/python3
RUN cd /tmp && wget https://bootstrap.pypa.io/get-pip.py && sync && python3 get-pip.py && rm get-pip.py
RUN pip3 install -U requests armada

ADD . /opt/microservice_python3

ENV PYTHONPATH /opt/microservice_python3/src
