# Mini Spark Broker Bootcamp

Welcome to the Apache Spark mini-broker bootcamp! We divided the work into 5 parts:

Using ZTF alerts:

* [Part1](bootcamp_1_lsst_alert_stream.ipynb): basics on the LSST alert system, and alerts (just documentation).
* [Part2](bootcamp_2_simple_connection.ipynb): connect the mini-broker to the stream with Apache Spark, and read ZTF alerts.
* [Part3](bootcamp_3_filtering.ipynb): manipulate the stream using simple filters.
* [Part4](bootcamp_4_external_classification.ipynb): Crossmatch objects of the stream with other catalog objects to operate an early classification.

Using LSST alerts (need external setup, see below):

* [Part5](bootcamp_5_LSST_alert.ipynb): connect the mini-broker to the stream with Apache Spark, and read LSST alerts.

## How to play the notebooks?

Long story short:

```bash
cd ${mini-spark-broker}

# Download a subset of ZTF data
./download_ztf_alert_data.sh

# Setup the containers
./setup_docker.sh

# Launch stream of alerts
./launch_alert_system.sh

# Launch the bootcamp (i.e. the notebook)
# and execute the notebooks!
./launch_bootcamp.sh
```

For more explanation, see below.

## Set up the environment

### Alert data set

We propose to play with a subset of the publicly available ZTF alerts ([website](https://ztf.uw.edu/alerts/public/)). There is a script at the root of this repo to download the data (see [download_ztf_alert_data.sh](../download_ztf_alert_data.sh)). For more information about the ZTF alert data, see [here](https://zwickytransientfacility.github.io/ztf-avro-alert/).

### Docker

To ease the use of the different components for the Alert System and the mini-broker, the bootcamp is played inside Docker containers (heavily inspired from the [lsst-dm/alert_stream](https://github.com/lsst-dm/alert_stream) repository!). Execute the [setup_docker.sh](../setup_docker.sh) script to initialise the Kafka server and the image containing the bootcamp.

## Launching the ZTF alert stream (Part 1-4)

In order to play with the bootcamp, you need first to create the stream of alerts. This is inspired by the [lsst-dm/alert_stream](https://github.com/lsst-dm/alert_stream) repository, maintained by the LSST DM group. Here are the steps you need:

```bash
###################################
# LSST Alert System
###################################
# See ../launch_alert_system.sh

# Send bursts of alerts at expected visit intervals to topic "ztf-stream":
docker run -it --rm \
    --network=mini_spark_broker_default \
    -v $PWD/data:/home/jovyan/work/data:ro \
    msb python bin/sendAlertStream.py kafka:9092 ztf-stream
```

At this stage the stream is created, and 499 alerts will be sent at 1 second interval between 2 alerts. No worry if it finishes before you started working, you will be able to consume them on a later time (and you can always relaunch the stream). If you see the stream processing in your console:

```bash
$ docker run -it --rm \
    --network=mini_spark_broker_default \
    -v $PWD/data:/home/jovyan/work/data:ro \
    msb python bin/sendAlertStream.py kafka:9092 ztf-stream
visit: 00150 	time: 1549289943.0019574
visits finished: 1 	 time: 1549289944.9786158
visit: 01150 	time: 1549289945.0016901
visits finished: 2 	 time: 1549289945.0222661
visit: 01150 	time: 1549289946.0018787
visits finished: 3 	 time: 1549289946.0292997
visit: 02150 	time: 1549289947.0036483
visits finished: 4 	 time: 1549289947.02289
visit: 02150 	time: 1549289948.0015655
visits finished: 5 	 time: 1549289948.0156095
visit: 02150 	time: 1549289949.0037196
visits finished: 6 	 time: 1549289949.017008
visit: 02150 	time: 1549289950.0042317
visits finished: 7 	 time: 1549289950.035189
visit: 04150 	time: 1549289951.002203
...
```

that means you can now start this bootcamp!

## Launching the Apache Spark mini-broker

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
# The name of the network is defined by the docker-compose
NETWORK=mini_spark_broker_default

# Run jupyter through the Docker
docker run -it --rm  \
	-v $PWD:/home/jovyan/work:rw -p 8888:8888 -p 4040:400 \
	--network=${NETWORK} -P msb \
	/usr/local/spark/bin/pyspark --packages ${KFKSTREAM},${KFKSQL}
```

Follow instructions on screen and start playing with the notebooks!

## Launching the LSST alert stream (Part 5)

In order to play with the [Part 5](bootcamp_5_LSST_alert.ipynb), you need to create the stream of alerts from LSST. This is very similar to the ZTF one we played with so far, with few modifications though. The best, in order to avoid any conflicting situation is to grab the official LSST alert stream repo and create the stream from it. Here are the steps to follow:

```bash
# Go to where you put user lib
# Clone the repo (make sure you have git-lfs to pull the data)
git clone https://github.com/lsst-dm/alert_stream.git

# Checkout current working branch
cd alert_stream && git checkout tickets/DM-17549

# Launch Zookeeper & Kafka servers
# Network name will be alert_stream_default
docker-compose up -d

# Build the container
docker build -t "alert_stream" .

# Launch the stream
docker run -it --rm \
    --network=alert_stream_default \
    -v $PWD/data:/home/alert_stream/data:ro \
    alert_stream python bin/sendAlertStream.py \
    kafka:9092 lsst-stream
```

From this point, a stream with 4 bursts of 10,000 alerts each will be created. Then launch the bootcamp with the `alert_stream_default` network.