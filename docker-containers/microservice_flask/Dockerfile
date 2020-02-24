FROM dockyard.armada.sh/microservice_python3
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV MICROSERVICE_FLASK_APT_GET_UPDATE_DATE 2020-02-21
RUN apt-get update -y

RUN apt-get install -y build-essential apache2 libapache2-mod-wsgi-py3

RUN pip3 install -U pip
RUN pip3 install -U requests armada Flask
RUN pip3 uninstall -y Werkzeug && pip install Werkzeug==0.16.1

# Apache configuration.
ADD ./apache2_vhost.conf /etc/apache2/sites-available/apache2_vhost.conf
RUN ln -s /etc/apache2/sites-available/apache2_vhost.conf /etc/apache2/sites-enabled/apache2_vhost.conf
RUN rm -f /etc/apache2/sites-enabled/000-default.conf

ADD ./supervisor/* /etc/supervisor/conf.d/
ADD . /opt/microservice_flask

EXPOSE 80
