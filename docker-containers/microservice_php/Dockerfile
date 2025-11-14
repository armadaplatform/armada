FROM microservice
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV MICROSERVICE_PHP_APT_GET_UPDATE_DATE 2015-05-25
ENV PHP_VERSION 5.6.40

# Install dependencies for building PHP from source
RUN apt-get update && apt-get install -y \
    apache2 \
    logrotate \
    build-essential \
    autoconf \
    libtool \
    bison \
    re2c \
    libxml2-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libmysqlclient-dev \
    libmcrypt-dev \
    libreadline-dev \
    libxslt1-dev \
    libzip-dev \
    apache2-dev \
    ca-certificates \
    wget

# Download and compile PHP 5.6 from source
RUN cd /tmp && \
    wget https://www.php.net/distributions/php-${PHP_VERSION}.tar.gz && \
    tar -xzf php-${PHP_VERSION}.tar.gz && \
    cd php-${PHP_VERSION} && \
    ./configure \
        --prefix=/usr/local/php5.6 \
        --with-config-file-path=/usr/local/php5.6/etc \
        --with-apxs2=/usr/bin/apxs2 \
        --enable-mbstring \
        --with-curl \
        --with-openssl \
        --with-openssl-dir=/usr \
        --with-libdir=lib/x86_64-linux-gnu \
        --with-xmlrpc \
        --enable-soap \
        --enable-zip \
        --with-gd \
        --with-jpeg-dir \
        --with-png-dir \
        --with-freetype-dir \
        --enable-mysqlnd \
        --with-mysqli=mysqlnd \
        --with-pdo-mysql=mysqlnd \
        --enable-opcache \
        --with-mcrypt \
        --with-readline \
        --with-xsl && \
    make -j$(nproc) && \
    make install && \
    mkdir -p /usr/local/php5.6/etc && \
    cp php.ini-production /usr/local/php5.6/etc/php.ini && \
    rm -rf /tmp/php-${PHP_VERSION}*

# Create symlinks for easier access
RUN ln -s /usr/local/php5.6/bin/php /usr/local/bin/php && \
    ln -s /usr/local/php5.6/bin/phpize /usr/local/bin/phpize && \
    ln -s /usr/local/php5.6/bin/php-config /usr/local/bin/php-config

# Create compatibility symlink for php5
RUN mkdir -p /etc/php/5.6 && ln -s /etc/php/5.6 /etc/php5

ADD ./supervisor/* /etc/supervisor/conf.d/

# Enable cron.
RUN apt-get install -y tzdata && echo "Etc/UTC" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

# Apache configuration - disable threaded MPMs and enable prefork for non-threadsafe PHP
RUN a2dismod mpm_event mpm_worker 2>/dev/null || true
RUN a2enmod mpm_prefork

# Create Apache runtime directory
RUN mkdir -p /var/run/apache2 && chown www-data:www-data /var/run/apache2

# Set ServerName to suppress warning
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Configure PHP in Apache - add PHP MIME type and handler
RUN echo "AddType application/x-httpd-php .php" >> /etc/apache2/apache2.conf && \
    echo "AddType application/x-httpd-php-source .phps" >> /etc/apache2/apache2.conf

# Enable necessary Apache modules
RUN a2enmod rewrite

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
