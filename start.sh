#!/bin/bash

set -euo pipefail
CWD="$(dirname $0)"

if [[ ! -d "$CWD/virtualenv" ]]; then
    cd $CWD && virtualenv virtualenv && pip install -r requirements.txt
fi

source "$CWD/virtualenv/bin/activate"

cd "$CWD" && gunicorn -c gunicorn.conf.py wsgi

exit 0
