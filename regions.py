# regions.py
#
# here's an attempt to sync the geographic timeseries
# using python! stick with python 2 for now
#
# USAGE
#
# python regions.py updateall
# which will update all regions over all possible dates
#
# python regions.py updateweek
# which will get the most recent wekk
#
# in the main file....can easily define a loop over other
# timeframes or specific regions
# (for a specific region, circumvent allregions)
#
# andy reagan
# 2015-02-04

import subprocess
import datetime
import os

regions = [["France","79","french",],["Germany","86","german",],["England","239","english",],["Spain","213","spanish",],["Brazil","32","portuguese",],["Mexico","145","spanish",],["South-Korea","211","korean",],["Egypt","69","arabic",],["Australia","14","english",],["New-Zealand","160","english",],["Canada","41","english",],["Canada-fr","41","french",],]

def processregion(region,date):
    # check the day file is there
    if not os.path.isfile('/usr/share/nginx/data/word-vectors/{0}/{1}-sum.csv'.format(region[0],datetime.datetime.strftime(date,'%Y-%m-%d'))):
        rsync(region,date)

    
    
def allregions(date):
    for region in regions:
        processregion(region,date)

def loopdates(startdate,enddate):
    while startdate <= enddate:
        allregions(startdate)
        startdate += datetime.timedelta(days=1)

def rsync(region,date):
    print "trying to get the file"
    if os.path.isdir('/usr/share/nginx/data/word-vectors/{0}'.format(region[0].lower())):
        # try to get the file
        subprocess.call("rsync -avzr vacc1:/users/a/r/areagan/fun/twitter/jake/pullTweets/word-vectors/{1}-{0}-word-vector.csv /usr/share/nginx/data/word-vectors/{2}/{1}-sum.csv".format(region[0],datetime.datetime.strftime(date,'%Y-%m-%d'),region[0].lower()),shell=True)
    else:
        os.mkdir('/usr/share/nginx/data/word-vectors/{0}'.format(region[0].lower()))
        subprocess.call("rsync -avzr vacc1:/users/a/r/areagan/fun/twitter/jake/pullTweets/word-vectors/{1}-{0}-word-vector.csv /usr/share/nginx/data/word-vectors/{2}/{1}-sum.csv".format(region[0],datetime.datetime.strftime(date,'%Y-%m-%d'),region[0].lower()),shell=True)

if __name__ == '__main__':

    # do the rsync
    start = datetime.datetime(2015,2,4)
    end = datetime.datetime.now()

    loopdates(start,end)
