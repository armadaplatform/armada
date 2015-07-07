FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN apt-get install -y python3 python3-dev build-essential

# Hack for broken pip. Replace it with 'apt-get install -y python3-pip' once it's fixed.
RUN wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py --no-check-certificate
RUN python3 get-pip.py
RUN ln -s /usr/local/bin/pip3 /usr/bin/pip3
RUN pip3 install -U requests

ADD . /opt/microservice_python3

ENV PYTHONPATH /opt/microservice_python3/src
