#!/bin/bash
green='\033[1;32m'
NC='\033[0m' # No Color.
echo -e "\n${green}Last 10 lines from every log file.${NC}"
tail -n 10 /var/log/supervisor/*
