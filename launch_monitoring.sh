#!/bin/bash
###################################
# LSST Alert System
###################################

docker build -t "msb" .

# Kafka dependencies
KFKSTREAM=org.apache.spark:spark-streaming-kafka-0-10-assembly_2.10:2.2.0
KFKSQL=org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0

# Send bursts of alerts at expected visit intervals to topic "my-stream":
docker run -it --rm \
    --network=mini_spark_broker_default \
    -v $PWD/data:/home/jovyan/work/data:ro \
    msb /usr/local/spark/bin/spark-submit --master local[*] \
    --packages ${KFKSTREAM},${KFKSQL} bin/monitorStream.py kafka:9092 ztf-stream 5
