#!/usr/bin/env bash

service redis-server restart

service supervisor restart

nginx -t
service nginx restart