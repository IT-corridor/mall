#!/bin/bash

NAME=mall_api
BASEDIR=/vagrant_data
DJANGODIR="${BASEDIR}/back"
SOCKFILE="/tmp/${NAME}.sock"
NUM_WORKERS=3
DJANGO_WSGI_MODULE="back.wsgi"
GUNICORN=gunicorn

cd $DJANGODIR

echo $USER

RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
exec $GUNICORN "${DJANGO_WSGI_MODULE}:application" \
  --env DJANGO_SETTINGS_MODULE=settings.local \
  --workers $NUM_WORKERS \
  --bind "unix:${SOCKFILE}" \
#  --user vagrant
