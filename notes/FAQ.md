# FAQ

**Once the stream is launched, how long the alerts will be available?**

Kafka keeps a copy of the alerts as long as it is live. So once you trigger a burst of alerts, those will be always available. If you shutdown the container of Kafka, all alerts will be lost.

**How many times should I relaunch the stream?**

Each time you launch the stream, 499 alerts are generated with 1 second interval between two alerts.
So if you want more alerts, relaunch the stream.

**Can I change the number of alerts?**

Feel free to download more data from the ZTF alerts [website](https://ztf.uw.edu/alerts/public/).

**Can I increase/decrease the interval between two alerts?**

Yes! Just set the `interval` variable in `bin/sendAlertStream.py`. Do not forget to build the docker image again for the change to be taken into account:

```bash
docker build -t "msb" .
```

**How can I simulate LSST-like alert schedule?**

LSST alert system will send ~10,000 alerts every 30 seconds. What you can do is:
* Download many many ZTF alerts (>> 10,000)
* Group alerts in pack of 10,000.
* Set interval between 2 alerts to be super short (ideally publish the 10,000 alerts in much less than 30 seconds!).
* Launch the stream every 30 seconds, sending alerts group-by-group.

# Troubleshooting

```bash
docker: Error response from daemon: network mini_spark_broker_default not found.
```
This usually means you did not set correctly the same network name for the two docker images.