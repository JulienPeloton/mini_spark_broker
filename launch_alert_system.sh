#!/bin/bash
###################################
# LSST Alert System
###################################

# Send bursts of alerts at expected visit intervals to topic "my-stream":
docker run -it --rm \
    --network=mini_spark_broker_default \
    -v $PWD/data:/home/jovyan/work/data:ro \
    msb python bin/sendAlertStream.py kafka:9092 ztf-stream
