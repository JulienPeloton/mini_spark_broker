FROM jupyter/pyspark-notebook
LABEL maintainer "peloton@lal.in2p3.fr"
ENV REFRESHED_AT 2019-02-01

# Add repo
WORKDIR /home/jovyan/work
ADD . .
ENV PYTHONPATH=$PYTHONPATH:/home/jovyan/work/python

# Add dependencies
RUN pip install -r requirements.txt

ENV PYSPARK_DRIVER_PYTHON=jupyter-notebook

WORKDIR /home/jovyan/work
