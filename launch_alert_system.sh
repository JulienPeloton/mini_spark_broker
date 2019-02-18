#!/bin/bash
###################################
# LSST Alert System
###################################

# Build the docker image (~6 GB!)
 # Slow the first time - super quick after.
 docker build -t "msb" .

# Send bursts of alerts at expected visit intervals to topic "my-stream":
docker run -it --rm \
    --network=mini_spark_broker_default \
    -v $PWD/data:/home/jovyan/work/data:ro \
    msb python bin/sendAlertStream.py kafka:9092 ztf-stream
