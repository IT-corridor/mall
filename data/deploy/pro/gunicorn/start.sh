#!/bin/bash

NAME=mall_api
BASEDIR=/home/django
DJANGODIR="${BASEDIR}/mall/back"
ENVDIR="${BASEDIR}/venv"
SOCKFILE="/tmp/${NAME}.sock"
NUM_WORKERS=3
DJANGO_WSGI_MODULE="back.wsgi"
GUNICORN=GUNICORN=${ENVDIR}/bin/gunicorn

cd $DJANGODIR
source "${ENVDIR}/bin/activate"

RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
exec $GUNICORN "${DJANGO_WSGI_MODULE}:application" \
  --env DJANGO_SETTINGS_MODULE=settings.local \
  --workers $NUM_WORKERS \
  --bind "unix:${SOCKFILE}" \
