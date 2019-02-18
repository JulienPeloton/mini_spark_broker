#!/usr/bin/env python
# Copyright 2018 Julien Peloton
# Author: Maria Patterson, Julien Peloton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Monitor Kafka stream received by Spark
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import window

import argparse
import glob
import time
import asyncio
import sys
import matplotlib
import matplotlib.pyplot as plt

from desc.msb import alertProducer, avroUtils
from desc.msb import monitoring

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'servers', type=str,
        help='Hostname or IP and port of Kafka broker producing stream.')
    parser.add_argument(
        'topic', type=str,
        help='Name of Kafka topic stream to read from.')
    parser.add_argument(
        'tinterval', type=int,
        help='Time between two stream monitoring.')
    args = parser.parse_args()

    # Grab the running Spark Session,
    # otherwise create it.
    spark = SparkSession \
        .builder \
        .appName("monitorStream") \
        .getOrCreate()

    # Create a DF from the incoming stream from Kafka
    # Note that <kafka.bootstrap.servers> and <subscribe>
    # must correspond to arguments of the LSST alert system.
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", args.servers) \
        .option("subscribe", args.topic) \
        .option("startingOffsets", "earliest") \
        .load()

    # We group data by partitions,
    # and count the number of alerts per partition
    # every 5 seconds.
    streamingCountsDF = (
      df.groupBy(
          "partition",
          window("timestamp", "1 seconds"))
        .count()
    )

    # keep the size of shuffles small
    spark.conf.set("spark.sql.shuffle.partitions", "2")

    # Trigger the streaming computation,
    # by defining the sink (memory here) and starting it
    countQuery = streamingCountsDF \
        .writeStream \
        .queryName("qcount")\
        .format("memory")\
        .outputMode("complete") \
        .start()

    colnames = ["inputRowsPerSecond", "processedRowsPerSecond", "timestamp"]

    count = 0
    matplotlib.rcParams.update({'font.size': 17})
    fig, ax = plt.subplots(figsize=(15,5))
    while True:
        try:
            monitoring.show_stream_process(ax, countQuery, colnames)
            plt.pause(5)
        except TypeError:
            print(
                """
                No Data to plot - Retyring ({} seconds)....
                server: {} / topic: {}
                """.format(count, args.servers, args.topic))
            plt.clf()
            time.sleep(5)
        count += 5


if __name__ == "__main__":
    main()
