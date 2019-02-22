FROM python:3.6
LABEL maintainer "peloton@lal.in2p3.fr"
ENV REFRESHED_AT 2019-02-22

# Add repo
WORKDIR /home/work
ADD . .
ENV PYTHONPATH=$PYTHONPATH:/home/work/python

# Add dependencies
RUN pip install -r requirements.txt

WORKDIR /home/work
