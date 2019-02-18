# Large-scale benchmark

## Alert system: Apache Kafka+Zookeeper cluster

We detail here the steps to fully configure the cluster for simulating the alert system. 

### Step 1: create a cluster with N machines in OpenStack. 

Setup:

* Image centos genericCloud 1809. 
* 1 master + 4 slaves (`N=5`).
* Volume `/data` 1 TB on each machine.

In our example, we have 5 machines with the following IP and names:

```bash
# in /etc/hosts
134.158.74.95 kafka-master
134.158.74.238 kafka-slave1
134.158.74.108 kafka-slave2
134.158.74.231 kafka-slave3
134.158.74.218 kafka-slave4
```

### Step 2: Setting environment on machines

**This procedure has to be repeated for each machine of the cluster**:

Create two folders in your home `libs` and `work`:

```bash
mkdir -p $HOME/libs
mkdir -p $HOME/work
ls $HOME
libs  work
```

Create two folders in `/data`:

```bash
mkdir -p /data/zookeeper
mkdir -p /data/kafka-logs
ls /data
kafka-logs  zookeeper
```

Install Java/Git/Python

```bash
# Java 8
sudo yum install java-1.8.0-openjdk-devel
# Git
sudo yum install git
# miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda
conda update -q conda
```

Update bash_profile

```bash
vi ~/.bash_profile
# Add this at the end
export PATH="$HOME/miniconda/bin:$PATH"
```

### Step 3: configuring Zookeeper

**The following has to be done only on the `login` machine (`kafka-master`)**:


[Download](https://kafka.apache.org/quickstart) Kafka and untar it in `$HOME/libs`:

```bash
cd $HOME/libs
wget http://mirrors.standaloneinstaller.com/apache/kafka/2.1.0/kafka_2.11-2.1.0.tgz
tar -xzf kafka_2.11-2.1.0.tgz
```

Go to Kafka folder, and edit the configuration file for Zookeeper:

```bash
cd $HOME/libs/kafka_2.11-2.1.0/conf
vi zookeeper.properties
```

Enter information about all machines:

```bash
# the directory where the snapshot is stored.
dataDir=/data/zookeeper
# the port at which the clients will connect
clientPort=24498
# disable the per-ip limit on the number of connections 
# since this is a non-production config
maxClientCnxns=60

# timeouts ZooKeeper uses to limit the length of 
# time the ZooKeeper servers in quorum have to connect to a leader
initLimit=5
# limits how far out of date a server can be from a leader
syncLimit=2

# server.X list the servers that make up the ZooKeeper service. 
# When the server starts up, it knows which server it is by looking 
# for the file myid in the dataDir directory. 
# That file has the contains the server number, in ASCII.
server.1=kafka-master:23333:23334
server.2=kafka-slave1:23333:23334
server.3=kafka-slave2:23333:23334
server.4=kafka-slave3:23333:23334
server.5=kafka-slave4:23333:23334
```

The `clientPort` (`24498`) and the two port numbers after each server name number (`23333` and `23334` in our case) must be opened (TCP).

**The following has to be done for all other machines (`kafka-slave${i}`)**:

Note that the entries of the form server.X list the servers that make up the ZooKeeper service. When the server starts up, it knows which server it is by looking for the file myid in the `dataDir` directory. That file has the contains the server number, in ASCII. So for each machine, you need to create this file:

```bash
# e.g. for kafka-master login machine
echo "1" > /data/zookeeper/myid

# e.g. for kafka-slave1 machine
ssh kafka-slave1
echo "2" > /data/zookeeper/myid
```

### Step 4: configuring Kafka

**The following has to be done only on all the machines**:

[Download](https://kafka.apache.org/quickstart) Kafka and untar it in `$HOME/libs`:

```bash
cd $HOME/libs
wget http://mirrors.standaloneinstaller.com/apache/kafka/2.1.0/kafka_2.11-2.1.0.tgz
tar -xzf kafka_2.11-2.1.0.tgz
```

Go to Kafka folder, and edit the configuration file for Kafka:

```bash
cd $HOME/libs/kafka_2.11-2.1.0/conf
vi server.properties
```

First in the `Server Basics` section, give unique broker ID per machine:

```bash
# The id of the broker. This must be set to a unique integer for each broker.
broker.id=0 # 0 for master, 1 for slave1, 2 for slave2, etc...
```

Then, update the `Socket Server Settings` with the login IP **of the machine**:

```bash
# The address the socket server listens on. It will get the value returned from
# java.net.InetAddress.getCanonicalHostName() if not configured.
#   FORMAT:
#     listeners = listener_name://host_name:port
#   EXAMPLE:
#     listeners = PLAINTEXT://your.host.name:9092
listeners=PLAINTEXT://xx.xx.xx.xx:24499
```
Note the port `24499` must be opened (TCP). Then change the data folder in `Log Basics`:

```bash
# A comma separated list of directories under which to store log files
log.dirs=/data/kafka-logs
```

Finally update the `Zookeeper` section with all machines and opened ports (see above):

```bash
# Zookeeper connection string (see zookeeper docs for details).
# This is a comma separated host:port pairs, each corresponding to a zk
# server. e.g. "127.0.0.1:3000,127.0.0.1:3001,127.0.0.1:3002".
# You can also append an optional chroot string to the urls to specify the
# root directory for all kafka znodes.
zookeeper.connect=kafka-master:24498,kafka-slave1:24498,kafka-slave2:24498,kafka-slave3:24498,kafka-slave4:24498
```

### Step 5: Finalizing configuration

Finally, for convenience, download Zookeeper and untar it in `$HOME/libs`:

```bash
cd $HOME/libs
wget http://mirror.cc.columbia.edu/pub/software/apache/zookeeper/zookeeper-3.4.10/zookeeper-3.4.10.tar.gz
tar -xvf zookeeper-3.4.10.tar.gz

# Copy server properties defined above
cp kafka_2.11-2.1.0/conf/zookeeper.properties zookeeper-3.4.10/conf/zoo.cfg
```

We will need the script to launch the servers (you can do it otherwise ny copying Kafka folder to all machines and launching zookeeper on all machines but that's real pain).


### Step 5: launching the alert system

```bash
# Launch Zookeeper from the login machine only
cd $HOME/libs/zookeeper-3.4.10
nohup ./bin/zkServer.sh start kafka_2.11-2.1.0/config/zookeeper.properties &
```

```bash
# Launch Kafka on all machines
ssh <machine>
cd $HOME/libs/kafka_2.11-2.1.0
nohup ./bin/kafka-server-start.sh config/server.properties &
```

```bash
# Install the mini_spark_broker
cd $HOME/work
git clone https://github.com/JulienPeloton/mini_spark_broker.git
cd mini_spark_broker
python bin/sendAlertStream.py \
134.158.74.95:24499,134.158.74.238:24499,\
134.158.74.108:24499,134.158.74.231:24499,\
134.158.74.218:24499 \
ztf-stream
```

## Broker: Apache Spark Cluster

Description to come

## Benchmarks

Description to come