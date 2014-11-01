# this job runs from cron every hour
# check to get the most recent parsed word vector from bluemoon

# for the vacc
# cd /users/s/t/storylab/website/data/hedonometer
# for linode
echo $(date)
cd /usr/share/nginx/data

DAY=$(date +%Y-%m-%d -d "yesterday")

python apicheck.py ${DAY}
