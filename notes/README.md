# Plans for a DESC Broker infrastructure using Apache Spark Streaming

The purpose of this document is twofold:

* Summarizing the LSST alert system developed by the LSST DM.
* Proposal and roadmap for DESC Broker Components and API that will connect to the LSST alert system stream.


![broker](system_design.png)

_Typical flow of alerts in astronomy. Raw data are collected by the telescope every nights, and alerts are issued by the Alert System. These alerts are streamed to other places, and treated by brokers (red). Brokers need to assess the relevance of the alerts, correlate corresponding alert data with external data (raw data or previous processed alerts for example) if needed, and produce scientific products for further analyses. Dashed lines represent stream processes._


## LSST alert system

### Definition

After each visit, and mainly based on image differencing, the LSST's alert-time Prompt Processing pipelines will report alerts. Alerts will be collected and issued as stream by the LSST alert system. Third-party community brokers will then receive the full stream of alerts and refine the selection of events of interest, extracting relevant scientfic events. However given the high volume of data to be transfered, only a limited number of brokers will be allowed to connect to the full stream of alerts. Therefore, a simple filtering service will also be provided by LSST for smaller use of the alert stream. In this note, we only focus on a community broker receiving the full stream of alerts.

Data processing leading to alerts will occur in the LSST Data Facility (LDF) at the National Center for Supercomputing Applications (NCSA) in Illinois, USA. The LDF also hosts the alert stream feeds to community brokers.

Note from the LDM-612: _Due to the need for Data Release Production-derived templates, Alert Production cannot run at full scale and full fidelity during commissioning nor the first year of operations. LSST DM is currently investigating options for Alert Production in year one._

### Anatomy of an alert: Apache Avro

The format chosen for the alert is Apache Avro. Each file has a JSON header containing the metadata, and data is serialised in a compact binary format.
An alert contains information about the dectection itself (ID, timestamp, ...) but also historical lightcurve, cutout images, timeseries features, and other contextual information. An alert is typically O(100) KB.

### Alert distribution: Apache Kafka

Apache Kafka is a distributed streaming platform. From our perspective (complete documentation [here](https://kafka.apache.org/documentation/)), that is a client of a Kafka cluster, the most relevant aspects of it are:

* Kafka publishes streams of records (= the alerts). 
* Kafka stores streams of records in a fault-tolerant durable way (= keep alive the alerts some time with guarantee it will not disappear). 
* For each stream of records, the Kafka cluster maintains a partitioned log (= alerts are distributed amond several machines).

In addition, two important properties:

* Communications between Kafka servers and the outside world are simply done using a language agnostic TCP protocol.
* The Kafka cluster durably persists all published records—whether or not they have been consumed—using a configurable retention period.


Kafka has its own naming of things. Here is an attemps to give definitions of most commonly used things, and relate those to LSST alert system components:

| Kafka name   | Kafka definition  | Corresponding LSST alert system object |
|--------------|--------------------------|---------------------------------|
| topic        | category or feed name to which records are published (= stream of records)    | category or feed name to which alerts are published (= stream of alerts)
| record       | an entry to the commit log. Each record consists of a key, a value, and a timestamp.             | alert

Topics in Kafka are always multi-subscriber; that is, a topic can have zero, one, or many consumers that subscribe to the data written to it.
Each partition is an ordered, immutable sequence of records that is continually appended to a structured commit log. The records in the partitions are each assigned a sequential `id` number called the `offset` that uniquely identifies each record within the partition. 

### Numbers and Requirements

#### Alert Stream size

Alerts are issued within 60 seconds of the shutter closure after each visit. Each visit produces O(10,000) alerts, each alert is O(100) KB, and there is O(30) seconds in between two visits. For 8 hours observation per night, this leads to a stream of O(1) TB per night.

#### Number of Brokers with full stream access

An allocation of 10 Gbps is baselined for alert stream transfer from the LDF. Given the alert stream size, this constrains the number brokers that can receive the full stream of alerts to a few.

#### Data retention periods

Keeping alert data available for some time is generally a good idea, as it allows a longer time window to analyse alerts if needed. All alerts will be stored in an archive in the DACs (incl. CC-IN2P3). *Need to know when this is updated/done and accessible*.

#### Shortest time to alert data products

A number of measurements will be stored at the alert moment in the Prompt Product Database (DIASource, etc.) and some others will be available within 24 hours (e.g. forced photometry, survey precovery for a limited number of objects, processed visit images). This service will be accessible through the LSST Science Platform.

<!--
### Launching Apache Kafka

#### Using Docker

A convenient way to create the stream and play with it is to use docker compose. In this way, you will be able to get two (or more) docker containers to talk to each other. One will be the producer, the other the consumer(s). All you need is to follow the README in the [lsst-dm/alert_stream](https://github.com/lsst-dm/alert_stream) repository [checked as of 29 Jan 2018].

#### On your local computer

You first need to [download](https://kafka.apache.org/documentation/#quickstart) Kafka. Extract the tar, move it to a safe location and launch Zookeeper and Kafka servers:

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties &
bin/kafka-server-start.sh config/server.properties &
```

The default configuration files should be fine for simple examples, though I invite you to have a look at it if you encounter network error later.

### Start playing: create a mock stream of LSST alerts with Kafka

Once Kafka is running, follow the steps in [lsst-dm/alert_stream](https://github.com/lsst-dm/alert_stream) to publish streams of alerts.

-->

## Designing a Broker for DESC

### What is a broker?

A Broker is primarily a filtering service: from a huge stream of alerts, it selects only alerts who are relevant for your science. Obviously defining what is relevant and what is no is not an easy task. 
So often Brokers offer a variety of services beyond simple yes/no filtering such as cross-matching or query services with another databases, tools to correlate alerts in time and to reconstruct signals spread over time, and so on.

Ultimately, we want a Broker to be able to _filter, aggregate, enrich, consume_ incoming Kafka topics (stream of alerts) or otherwise _transform_ into new topics for further consumption or follow-up processing. From LDM-612, a broker may include:

1. redistributing alert packets
2. filtering alerts
3. cross-correlating LSST alerts with other static catalogs or alert stream
4. classifying events scientifically
5. providing user interfaces to the data
6. coordinating scientific activity among collaborators
7. triggering followup observing
8. for users with appropriate data rights, facilitating followup queries and/or user-generated processing within the LSST Data Access Center
9. managing annotation & citation as followup observations are made
10. collecting classification and other information gathered by the scientific community

Hereafter in this bootcamp, we will focus on 2 and 3. Other functions will be discussed and implemented later (but definitely doable!).

### Motivation: simplicity, scalability & flexibility

What is driving the design of the broker? 

* The broker should be simple enough to be used by a majority of scientists and maintained in real-time. This means the exposed API must be easily understood by anyone, and the code base should be as small as possible to allow easy maintenance and upgrade. 
* The broker's behaviour should be the same regardless the amount of incoming data. This implies the technology used for this is scalable.
* The broker structure should allow for easy extension. As data will come, new features will be added, and the broker should be able to incorporate those smoothly. In addition, the broker should be able to connect to a large numbers of external tools and frameworks to maximize its scientific production without redeveloping tools.

The solution we propose here is [Apache Spark](http://spark.apache.org/), and more specifically its [streaming module](http://spark.apache.org/streaming/). The language chosen for the API is Python, which is widely used in the astronomy community, has a large scientific ecosystem and easily connects with LSST DESC existing tools.

### Spark Streaming & Kafka: basics

Note: _The Kafka project introduced a new consumer API between versions 0.8 and 0.10, so there are 2 separate corresponding Spark Streaming packages available. See [here](https://spark.apache.org/docs/2.3.1/streaming-kafka-integration.html) for more information._

For a broker it isn't enough to just read, write, and store streams of data. In our case the purpose is to enable real-time processing of streams as described above. It would be possible to use directly a Kafka cluster for the broker as well to do simple processing (aggregation, join), but eventually we want to be able to do something more sophisticated, like running more traditional analyses (i.e. non-trivial processing) on the alert data in real-time.

#### Streaming + DataFrames (new API)

[structured-streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html): processing structured data streams with relation queries (using Datasets and DataFrames, newer API than DStreams). So in a sense Spark Streaming+SQL modules. (for kafka-related stuff: [structured-streaming-kafka](https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html))

### Proof-of-concept: connecting to LSST alert stream with Spark

We set up a small bootcamp to put hands on the broker! Materials can be found [here](https://github.com/JulienPeloton/mini_spark_broker).

### Going beyond: Machine learning

### Going beyond: connecting to external databases

#### Retrieving Template and Calibration Images, Science Images, DIASources, DIAObject, and DRP Objects

LSST Science Platform provides access to proprietary data products.
a number of measurements (e.g. forced photometry, survey precovery for a limited number of objects, processed visit images) will be stored at the alert moment in the Prompt Product Database and will be available within 24 hours. This service will be accessible through the LSST Science Platform.

https://dmtn-092.lsst.io/

### Front-end: AstroLabNet

### Which science?

That's your job!

## References

Reference documents mentionning the LSST alert system:

* LDM-612: Plans and Policies for LSST Alert Distribution: [repo](https://github.com/lsst/LDM-612)
* DMTN-028: Benchmarking a distribution system for LSST alerts: [webpage](https://dmtn-028.lsst.io/)
* DMTN-081: Deploying an alert stream mini-broker prototype: [webpage](https://dmtn-081.lsst.io/)
* DMTN-092: Alert Production Pipeline Interfaces: [webpage](https://dmtn-092.lsst.io/)
* DMTN-093: Design of the LSST Alert Distribution System: [webpage](https://dmtn-093.lsst.io/)

Apache ecosystem tools used here:

* Apache Kafka: [webpage](https://kafka.apache.org/)
* Apache Avro: [webpage](https://avro.apache.org/)
* Apache Spark: [webpage](https://spark.apache.org/)

Useful code repositories:

* LSST DM GitHub repository for an alert system prototype: [repo](https://github.com/lsst-dm/alert_stream)
* Bootcamp for the broker: [repo](https://github.com/JulienPeloton/mini_spark_broker)
