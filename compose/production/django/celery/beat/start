#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset


celery -A taskapp beat -l INFO
