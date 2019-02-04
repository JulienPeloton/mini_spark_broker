# Mini Spark Broker

Welcome to the Mini Spark broker!

**Goals for this study:**

The purpose of this repo is to test Spark Streaming capability in the context of the DESC Broker design. More specifically:

* Summarizing the LSST alert system developed by the LSST DM in the context of the DESC broker initiative.
* Get familiar with the Apache Spark Streaming module through a simple bootcamp.
* Help to formulate a proposal and define a roadmap for DESC Broker Components and API that will connect to the LSST alert system stream.

![broker](notes/system_design.png)

_Typical flow of alerts in astronomy. Raw data are collected by the telescope every nights, and alerts are issued by the Alert System. These alerts are streamed to other places, and treated by brokers (red). Brokers need to assess the relevance of the alerts, correlate corresponding alert data with external data (raw data or previous processed alerts for example) if needed, and produce scientific products for further analyses. Dashed lines represent stream processes._
 
 
**Resources**

* [Notes](notes/) concerning the LSST alert system, the DESC broker, and Apache Spark. It also contains slides summarizing this study, and a FAQ.
* [Bootcamp](notebooks/) to play with a mini-broker using the Apache Spark Streaming module.
* [Scripts](bin/) containing LSST alert system simulator and the mini-broker launcher scripts.
* [Library](python/) containing various functions and classes for the alert simulator and the mini-broker.