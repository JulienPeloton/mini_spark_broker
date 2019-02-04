#!/bin/bash

# Launch Zookeeper and Kafka servers (need once!)
docker-compose up -d
# `docker-compose down` to shut them down.

# Build the docker image (~6 GB!)
# Slow the first time - super quick after.
docker build -t "msb" .
