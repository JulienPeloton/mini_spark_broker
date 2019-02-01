# Mini Spark Broker Bootcamp

Welcome to the Mini Spark broker bootcamp!

* [Part1](bootcamp_1_lsst_alert_stream.ipynb): basics on the LSST alert system, and alerts.
* [Part2](bootcamp_2_simple_connection.ipynb): connect the mini-broker to the stream with Apache Spark, and read alerts.
* [Part3](bootcamp_3_filtering.ipynb): manipulate the streams using simple filters.
* [Part4](bootcamp_4_crossmatching.ipynb): Crossmatch objects of the stream with other catalog objects.

## Launching the alert stream

In order to play with the bootcamp, you need first to create the stream of alerts. This is handled by the [lsst-dm/alert_stream](https://github.com/lsst-dm/alert_stream) repository, maintained by the LSST DM group. Here are the steps you need:

```bash
###################################
# LSST Alert System
###################################

# clone the repo (need once!)
git clone https://github.com/lsst-dm/alert_stream.git
cd alert_stream

# Launch Zookeeper and Kafka servers (need once!)
docker-compose up -d
# `docker-compose down` to shut them down.

# Build the alert stream image
docker build -t "alert_stream" .

# Send bursts of alerts at expected visit intervals to topic "my-stream":
docker run -it --rm \
    --network=alert_stream_default \
    -v $PWD/data:/home/alert_stream/data:ro \
    alert_stream python bin/sendAlertStream.py kafka:9092 my-stream
```

At this stage the stream is created, and 4 alerts will be sent at ~30 seconds interval. No worry if it finishes before you started working, you will be able to consume them on a later time (and you can always relaunch the stream).

## Launching the mini Spark broker

Once the alert stream container is running, open a new terminal window and start the mini broker container:

```bash
###################################
# Mini Spark Broker
###################################
# See ../launch_bootcamp.sh

# Build the docker image (~6 GB!)
# Slow the first time - super quick after.
docker build -t "msb" .

# Kafka dependencies
KFKSTREAM=org.apache.spark:spark-streaming-kafka-0-10-assembly_2.10:2.2.0
KFKSQL=org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0

# Network used by the alert system
NETWORK=alert_stream_default

# Run jupyter through the Docker
docker run -it --rm  \
	-v $PWD:/home/jovyan/work:rw -p 8888:8888 -p 4040:400 \
	--network=${NETWORK} -P msb \
	/usr/local/spark/bin/pyspark --packages ${KFKSTREAM},${KFKSQL}
```

Follow instructions on screen and start playing with the notebooks!

## Troubleshooting

```bash
docker: Error response from daemon: network alert_stream_default not found.
```
This usually means you did not start the container for the alert stream (see [Part1](bootcamp_1_lsst_alert_stream.ipynb)), or did not set correctly the same network name for the two docker images.