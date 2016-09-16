#!/usr/bin/env bash

apt-get update
# install system requirements
apt-get install -y nginx postgresql redis-server libpq-dev \
    libtiff5-dev libjpeg8-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev \
	python-setuptools python-dev supervisor

# install python pip and python packages
easy_install pip
pip install -r /vagrant_data/requirements.txt

rm -rf /var/lin/apt/lists/*


# coping uwsgi files to /etc:
cp -r /vagrant_data/deploy/local/supervisor/* /etc/supervisor/conf.d/

# coping uwsgi service file to systemd:
#ln -s /vagrant_data/uwsgi.service /etc/systemd/system/


# Nginx!
# If you want to
#ln -s /vagrant_data/nginx/first /etc/nginx/sites-enabled/first
cp -r /vagrant_data/deploy/nginx/* /etc/nginx/
cp -r /vagrant_data/deploy/local/nginx/* /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Cleaning
apt-get -y autoremove
apt-get -y clean
