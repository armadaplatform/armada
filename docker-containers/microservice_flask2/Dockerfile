FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV MICROSERVICE_FLASK_APT_GET_UPDATE_DATE 2018-03-26
RUN apt-get update -y

RUN apt-get install -y python3 python3-dev python3-pip build-essential apache2 libapache2-mod-wsgi-py3

RUN pip3 install -U pip
RUN pip3 install -U requests armada Flask

# Apache configuration.
ADD ./apache2_vhost.conf /etc/apache2/sites-available/apache2_vhost.conf
RUN ln -s /etc/apache2/sites-available/apache2_vhost.conf /etc/apache2/sites-enabled/apache2_vhost.conf
RUN rm -f /etc/apache2/sites-enabled/000-default.conf

ADD ./supervisor/* /etc/supervisor/conf.d/
ADD . /opt/microservice_flask

EXPOSE 80
