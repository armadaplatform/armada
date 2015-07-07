FROM microservice_python
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN pip install -U web.py

# Uncomment following line to tell hermes, that you want to use configuration stored locally, in this case - in "config" subdirectory, relative to Dockerfile
# ENV CONFIG_DIR ./config

ADD . /opt/_MICROSERVICE_PYTHON_TEMPLATE_
ADD ./supervisor/_MICROSERVICE_PYTHON_TEMPLATE_.conf /etc/supervisor/conf.d/_MICROSERVICE_PYTHON_TEMPLATE_.conf

EXPOSE 80
