#!/usr/bin/env bash

set -e

cd `dirname $0`/..
source /home/ubuntu/mbta_service/virtualenv/bin/activate
source /home/ubuntu/mbta_service/secure.sh

cd /home/ubuntu/mbta_service/mbta
export PYTHONPATH=/home/ubuntu/mbta_service/mbta/src
pip install -r requirements.txt

gunicorn --bind=unix:/tmp/gunicorn.sock --workers=4 server:app
