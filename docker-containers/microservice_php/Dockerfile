FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV MICROSERVICE_PHP_APT_GET_UPDATE_DATE 2015-05-25
RUN LC_ALL=C.UTF-8 add-apt-repository ppa:ondrej/php
RUN apt-get update
RUN apt-get install -y apache2 php5.6 php5.6-mysql php5.6-curl php5.6-mbstring

RUN ln -s /etc/php/5.6 /etc/php5

ADD ./supervisor/* /etc/supervisor/conf.d/

# Enable cron.
RUN echo "Etc/UTC" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

# Apache configuration.
ADD ./apache2_vhost.conf /etc/apache2/sites-available/apache2_vhost.conf
RUN ln -s /etc/apache2/sites-available/apache2_vhost.conf /etc/apache2/sites-enabled/apache2_vhost.conf
RUN rm -f /etc/apache2/sites-enabled/000-default.conf
RUN echo "StartServers 1\nMinSpareServers 1\nMaxSpareServers 3" >> /etc/apache2/apache2.conf

ADD . /opt/microservice_php
RUN chmod +x /opt/microservice_php/run_apache2.sh

# Remove old session files
RUN (crontab -l; echo "0 2 * * * /usr/lib/php/sessionclean") | crontab -

EXPOSE 80
