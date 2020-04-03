#!/bin/bash
source /var/lib/jenkins/hedonometer_secrets.sh
export PYTHONPATH="$PYTHONPATH:/home/prod/app"
export DJANGO_SETTINGS_MODULE="mysite.settings"
python3.8 regions.py --start-date ${START_DATE}
