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
"""Generates batches of alerts coming from ZTF.
"""
import argparse
import glob
import time
import asyncio
from lsst.msb import alertProducer, avroUtils

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'broker', type=str,
        help='Hostname or IP and port of Kafka broker.')
    parser.add_argument(
        'topic', type=str,
        help='Name of Kafka topic stream to push to.')
    args = parser.parse_args()

    # Configure producer connection to Kafka broker
    conf = {'bootstrap.servers': args.broker}
    streamProducer = alertProducer.AlertProducer(
        args.topic, schema_files=None, **conf)

    # Scan for avro files
    root = "./data"
    files = [f for f in glob.glob("/".join([root, "*.avro"]))]
    files.sort()

    def send_visit(f):
        print('visit:', f[15:20], '\ttime:', time.time())
        # Load alert contents
        with open(f, mode='rb') as file_data:
            # Read the data
            data = avroUtils.readSchemaData(file_data)

            # Read the Schema
            schema = data.schema

            # Send the alerts
            alert_count = 0
            for record in data:
                if alert_count < 10000:
                    streamProducer.send(
                        record, alert_schema=schema, encode=True)
                    alert_count += 1
                else:
                    break
        streamProducer.flush()

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(
        alertProducer.schedule_delays(loop, send_visit, files, interval=1))
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    main()
