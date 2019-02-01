FROM jupyter/pyspark-notebook
LABEL maintainer "peloton@lal.in2p3.fr"
ENV REFRESHED_AT 2019-02-01

# Basic tools
#RUN apt-get update && \
# apt-get install vim

# Get alert schemas. # TODO update to checkout master when schema is updated
WORKDIR /home/jovyan
RUN git clone https://github.com/lsst-dm/sample-avro-alert.git && cd sample-avro-alert && git checkout tickets/DM-8160

# Get alert stream utils
WORKDIR /home/jovyan
RUN git clone https://github.com/lsst-dm/alert_stream.git
ENV PYTHONPATH=$PYTHONPATH:/home/alert_stream/python

# Add other dependencies
WORKDIR /home/jovyan/work
ADD requirements.txt .
RUN pip install -r requirements.txt

ENV PYSPARK_DRIVER_PYTHON=jupyter-notebook

WORKDIR /home/jovyan/work
