#!/bin/bash -x

set -eo pipefail
CWD="$(dirname $0)"

if [ ! -d "$CWD/virtualenv" ]; then
    cd "$CWD" && virtualenv virtualenv
fi

source "$CWD/virtualenv/bin/activate"

pip install -r requirements.txt

cd "$CWD" && gunicorn -c gunicorn.conf.py wsgi

exit 0
