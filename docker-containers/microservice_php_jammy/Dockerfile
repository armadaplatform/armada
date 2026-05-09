FROM microservice_jammy
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN apt-get update
RUN apt-get install -y apache2 logrotate php8.1 php8.1-mysql php8.1-curl php8.1-mbstring php8.1-zip wget

RUN ln -s /etc/php/8.1 /etc/php8

ADD ./supervisor/* /etc/supervisor/conf.d/

# Enable cron.
RUN echo "Etc/UTC" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

# Apache configuration.
ADD ./apache2_vhost.conf /etc/apache2/sites-available/apache2_vhost.conf
RUN ln -s /etc/apache2/sites-available/apache2_vhost.conf /etc/apache2/sites-enabled/apache2_vhost.conf
RUN rm -f /etc/apache2/sites-enabled/000-default.conf
RUN echo "StartServers 1\nMinSpareServers 1\nMaxSpareServers 3" >> /etc/apache2/apache2.conf

# Remove old session files
RUN (crontab -l; echo "0 2 * * * /usr/lib/php/sessionclean") | crontab -

# Enable logrotate
RUN useradd syslog
RUN (crontab -l; echo "@daily /usr/sbin/logrotate /etc/logrotate.conf") | crontab -

ADD . /opt/microservice_php
RUN chmod +x /opt/microservice_php/run_apache2.sh

EXPOSE 80
