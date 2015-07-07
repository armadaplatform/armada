#!/bin/bash

echo export MICROSERVICE_NAME="${MICROSERVICE_NAME}" >> /etc/apache2/envvars
echo export MICROSERVICE_ENV="${MICROSERVICE_ENV}" >> /etc/apache2/envvars
echo export MICROSERVICE_APP_ID="${MICROSERVICE_APP_ID}" >> /etc/apache2/envvars
echo export CONFIG_PATH="${CONFIG_PATH}" >> /etc/apache2/envvars

service apache2 start
