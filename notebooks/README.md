# Mini Spark Broker Bootcamp

Welcome to the Mini Spark broker bootcamp!

* [Part1](bootcamp_1_lsst_alert_stream.ipynb): basics on the LSST alert system, and alerts.
* [Part2](bootcamp_2_simple_connection.ipynb): connect the mini-broker to the stream with Apache Spark, and read alerts.
* [Part3](bootcamp_3_filtering.ipynb): manipulate the streams using simple filters.
* [Part4](bootcamp_4_crossmatching.ipynb): Crossmatch objects of the stream with other catalog objects.

## Set up the environment

### Alert data set

We propose to play with a subset of the publicly available ZTF alerts ([website](https://ztf.uw.edu/alerts/public/)). There is a script at the root of this repo to download the data (see [download_data.sh](../download_data.sh)). For more information about the ZTF alert data, see [here](https://zwickytransientfacility.github.io/ztf-avro-alert/).

### Docker

To ease the use of the different components for the Alert System and the mini-broker, the bootcamp is played inside Docker containers (heavily inspired from the [lsst-dm/alert_stream](https://github.com/lsst-dm/alert_stream) repository!). Execute the [setup_docker.sh](../setup_docker.sh) script to initialise the Kafka server and the image containing the bootcamp.

## Launching the alert stream

In order to play with the bootcamp, you need first to create the stream of alerts. This is inspired by the [lsst-dm/alert_stream](https://github.com/lsst-dm/alert_stream) repository, maintained by the LSST DM group. Here are the steps you need:

```bash
###################################
# LSST Alert System
###################################
# See ../launch_alert_system.sh

# Send bursts of alerts at expected visit intervals to topic "my-stream":
docker run -it --rm \
    --network=mini_spark_broker_default \
    -v $PWD/data:/home/jovyan/work/data:ro \
    msb python bin/sendAlertStream.py kafka:9092 my-stream
```

At this stage the stream is created, and 499 alerts will be sent at ~10 seconds interval. No worry if it finishes before you started working, you will be able to consume them on a later time (and you can always relaunch the stream).

## Launching the mini Spark broker

Once the alert stream container is running, open a new terminal window and start the mini broker container:

```bash
###################################
# Mini Spark Broker
###################################
# See ../launch_bootcamp.sh

# Kafka dependencies
KFKSTREAM=org.apache.spark:spark-streaming-kafka-0-10-assembly_2.10:2.2.0
KFKSQL=org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0

# Network used by the alert system
NETWORK=mini_spark_broker_default

# Run jupyter through the Docker
docker run -it --rm  \
	-v $PWD:/home/jovyan/work:rw -p 8888:8888 -p 4040:400 \
	--network=${NETWORK} -P msb \
	/usr/local/spark/bin/pyspark --packages ${KFKSTREAM},${KFKSQL}
```

Follow instructions on screen and start playing with the notebooks!
