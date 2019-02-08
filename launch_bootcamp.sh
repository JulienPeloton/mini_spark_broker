#!/bin/bash

# Build the docker image (~6 GB!)
# Slow the first time - super quick after.
docker build -t "msb" .

# Kafka dependencies
KFKSTREAM=org.apache.spark:spark-streaming-kafka-0-10-assembly_2.10:2.2.0
KFKSQL=org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0

# Network used by the alert system
NETWORK=mini_spark_broker_default

# Run jupyter through the Docker
docker run -it --rm  \
	-v $PWD:/home/jovyan/work:rw -p 8888:8888 -p 400:4040 \
	--network=${NETWORK} -P msb \
	/usr/local/spark/bin/pyspark --packages ${KFKSTREAM},${KFKSQL}
