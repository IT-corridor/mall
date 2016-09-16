#!/usr/bin/env bash

service supervisor restart
supervisorctl update

nginx -t
service nginx restart