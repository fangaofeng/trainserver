#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset


celery -A taskapp worker -l INFO
