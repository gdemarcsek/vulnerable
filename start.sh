#!/bin/bash -x

set -eo pipefail
CWD="$(dirname $0)"

if [ ! -d "$CWD/virtualenv" ]; then
    cd "$CWD" && virtualenv --system-site-packages virtualenv
fi

source "$CWD/virtualenv/bin/activate"

cd "$CWD"
pip install -r requirements.txt

export PYTHONNOUSERSITE=1
export PYTHONUSERBASE=1
exec gunicorn -c gunicorn.conf.py wsgi
