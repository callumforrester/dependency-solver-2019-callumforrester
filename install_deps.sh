#!/bin/bash
apt-get update
apt-get install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y python3.7 python-virtualenv

. venv/bin/activate
pip install -r requirements.txt
