#!/bin/bash -x

set -eo pipefail
CWD="$(dirname $0)"

if [ ! -d "$CWD/virtualenv" ]; then
    cd "$CWD" && virtualenv virtualenv
fi

source "$CWD/virtualenv/bin/activate"

cd "$CWD"
pip install -r requirements.txt
python -s $(which gunicorn) -c gunicorn.conf.py wsgi

exit 0
