source /home/prod/.env
cd /usr/share/nginx/data
export PYTHONPATH="$PYTHONPATH:/home/prod/app"
export DJANGO_SETTINGS_MODULE="mysite.settings"
python regions.py
