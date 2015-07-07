#!/bin/sh
yellow='\033[1;33m'
cyan='\033[1;36m'
green='\033[1;32m'
purple='\033[1;35m'
red='\033[1;31m'
gold='\033[0;33m'
NC='\033[0m' # No Color.
echo -e "\n${yellow}Environment variables${NC}"

if [ -f /var/opt/armada_environment.sh ]; then
    VARS=( `cat /var/opt/armada_environment.sh | sort` )
    printf -- '%s\n' "${VARS[@]}"

    for VAR in ${VARS[@]}
    do
        parts=(${VAR//\"/ })
        if [ ${parts[0]} == "ARMADA_RUN_COMMAND=" ]; then
                decoded=`python -mbase64 -d <<< ${parts[1]}`
                echo -e "\n${parts[0]}${gold} ${decoded}${NC}"
        fi
        if  [ ${parts[0]} == "RESTART_CONTAINER_PARAMETERS=" ]; then
            decoded=`python -mbase64 -d <<< ${parts[1]} | python -mjson.tool`
            echo -e "\n${parts[0]}${gold} ${decoded} ${NC}"
        fi
    done

else
    # For old images (before 09-01-2015 merge).
    cat /etc/bash.bashrc | grep export | awk '{print $2;}' | sort
fi

echo -e "\n${cyan}Available hermes configs ${NC}"
cd /etc/opt ; find -L . -maxdepth 1 -type d | sort

echo -e "\n${green}Last health check ${NC}"
cat /var/log/supervisor/run_health_checks-stderr*log | grep "$(cat /var/log/supervisor/run_health_checks-stderr*log | grep '^=== START: ' | tail -n1)" -A 100

echo -e "\n${purple}Process tree ${NC}"
ps -auxf

echo -e "\n${red}Open ports ${NC}"
netstat -nltupw
