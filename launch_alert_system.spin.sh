#!/bin/bash
###################################
# LSST Alert System for Spin
###################################
set -e

# Build the docker image (~6 GB!)
# Slow the first time - super quick after.
docker build -t "msbspin" -f Dockerfile.spin .

# Should be somewhere on /global/project or $HOME.
DATADIR=

# Send bursts of alerts at expected visit intervals to topic "my-stream":
docker run -it --rm \
    --network=mini_spark_broker_default \
    -v ${DATADIR}:/home/work/data:ro \
    msbspin python bin/sendAlertStream.py kafka:9092 ztf-stream
