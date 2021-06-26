#!/usr/bin/env bash

# Run this script on a fresh AWS EC2 instance. The setup process was tested using a Lightsail instance with the
# following:
#  - 512 MB RAM, 1 vCPU, 20 GB SSD.
#  - Lightsail Static IP.
#  - DNS A record registered and pointing to the static IP.

DOMAIN=mbta.mcgachey.org
EMAIL=phil@mcgachey.net

sudo apt update
sudo apt upgrade
sudo apt install -y python3-venv redis-server snapd

# The service has the following structure:
# ~/mbta_service
#      -> mbta        <-- Checked out from Github
#      -> secure.sh   <-- Uploaded by the deploy script (not stored in Github)
#      -> virtualenv  <-- Not strictly necessary since there's only one service running on the host, but helps to keep
#                         things consistent with the local dev environment
mkdir ~/mbta_service
python3 -m venv ~/mbta_service/virtualenv
git clone https://github.com/mcgachey/mbta.git

# Create a system service to run the web app
sudo cp ~/mbta_service/mbta/bin/mbta.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mbta
sudo systemctl start mbta

# Grab an SSL certificate from LetsEncrypt
sudo snap install snap-store
sudo snap install --classic certbot
sudo certbot certonly --standalone --preferred-challenges http-01 -m $EMAIL --agree-tos --non-interactive -d $DOMAIN
# Set the certificate to auto-renew
sudo crontab ~/mbta_service/mbta/bin/crontab

# Configure Nginx to proxy the app
sudo apt install -y nginx
sudo cp ~/mbta_service/mbta/bin/nginx_site /etc/nginx/sites-available/mbta
cd /etc/nginx/sites-enabled/
sudo rm default
sudo ln -s /etc/nginx/sites-available/mbta
sudo nginx -t
sudo service nginx reload
