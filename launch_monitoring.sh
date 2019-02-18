#!/bin/bash
###################################
# Monitor the stream (non-docker version)
###################################

# Kafka dependencies
KFKSTREAM=org.apache.spark:spark-streaming-kafka-0-10-assembly_2.10:2.2.0
KFKSQL=org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0

# Kafka producer stream location
IPPORT="134.158.74.95:24499"
MASTER="local[*]"

# Send bursts of alerts at expected visit intervals to topic "my-stream":
spark-submit --master ${MASTER} \
    --packages ${KFKSTREAM},${KFKSQL} \
    bin/monitorStream.py ${IPPORT} ztf-stream 5
