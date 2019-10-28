#!/bin/sh

set -o errexit
set -o nounset


rm -f './celerybeat.pid'
celery -A taskapp beat -l INFO
