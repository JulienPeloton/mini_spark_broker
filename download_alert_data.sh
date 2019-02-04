#!/bin/bash

# Data will be stored at data/
mkdir -p data
cd data/

# Download subset of ZTF public data - 22 MB (zipped)
wget https://ztf.uw.edu/alerts/public/ztf_public_20181129.tar.gz

# Untar the alert data - 55 MB
tar -zxvf ztf_public_20181129.tar.gz

