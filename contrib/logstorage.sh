#! /bin/bash                                                                                                                                                 
SCRIPTDIR="$(cd "$(dirname "$0")"; pwd)"

python $SCRIPTDIR/../manage.py logstorage
