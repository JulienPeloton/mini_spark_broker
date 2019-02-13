#!/bin/bash

# Force the script to exit in case of error
# this will tell the user either docker-compose
# or docker is not correctly set-up.
set -e

# Launch Zookeeper and Kafka servers (need once!)
docker-compose up -d
# `docker-compose down` to shut them down.

# Build the docker image (~6 GB!)
# Slow the first time - super quick after.
docker build -t "msb" .
