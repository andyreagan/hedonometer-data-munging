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

from numpy import zeros, array
from labMTsimple.storyLab import *
import subprocess
import datetime
import os
import sys
import copy
import codecs
import re

regions = [["France","79","french",],["Germany","86","german",],["England","239","english",],["Spain","213","spanish",],["Brazil","32","portuguese",],["Mexico","145","spanish",],["South-Korea","211","korean",],["Egypt","69","arabic",],["Australia","14","english",],["New-Zealand","160","english",],["Canada","41","english",],["Canada-fr","41","french",],]

def processregion(region,date):
    # check the day file is there
    if not os.path.isfile('/usr/share/nginx/data/word-vectors/{0}/{1}-sum.csv'.format(region[0],datetime.datetime.strftime(date,'%Y-%m-%d'))):
        rsync(region,date)

    # add up the previous vectors
    rest('prevvectors',date,date,region)

    timeseries('append',date,date,region,useStopWindow=True)
    
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

def sumfiles(start,end,wordvec,lang,numw):
    curr = copy.copy(start)
    while curr <= end:
        # print "adding {0}".format(curr.strftime('%Y-%m-%d'))
        try:
            f = open('word-vectors/{1}/{0}-sum.csv'.format(curr.strftime('%Y-%m-%d'),lang),'r')
            tmp = f.read().split('\n')
            f.close()
            while len(tmp) > numw:
                del(tmp[-1])
            wordvec=wordvec+array(map(int,tmp))
        except:
            print "could not load {0}".format(curr.strftime('%Y-%m-%d'))
            print 'could not load word-vectors/{1}/{0}-sum.csv'.format(curr.strftime('%Y-%m-%d'),lang)
            # raise 
        curr+=datetime.timedelta(days=1)

    return wordvec,curr

def rest(option,start,end,region,outfile='test.csv',days=[]):
    # if the option is range, pass it an outfile to write to
    # if the option is list, pass it an outfile and days list
    if option == 'prevvectors':
        labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+region[2]+'.txt',returnVector=True)
        numw = len(labMTvector)

        maincurr = copy.copy(start+datetime.timedelta(days=-1))
        while maincurr<end:
            wordvec = zeros(numw)
            # added the try loop to handle failure inside the sumfiles
            # try:
            [total,date] = sumfiles(maincurr+datetime.timedelta(days=-6),maincurr+datetime.timedelta(days=0),wordvec,region[0].lower(),numw)
            
            # write the total into a file for date
            print "printing to {0}-prev7.csv".format(date.strftime('%Y-%m-%d'))
            f = open('word-vectors/{1}/{0}-prev7.csv'.format(date.strftime('%Y-%m-%d'),region[0].lower()),'w')
            for i in xrange(numw):
                f.write('{0:.0f}\n'.format(total[i]))
            f.close()
            # except:
            #     print "failed on {0}".format(date.strftime('%Y-%m-%d'))
            #     print "-------------------------------"
            maincurr+=datetime.timedelta(days=1)

    if option == 'range':
        labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+region[2]+'.txt',returnVector=True)
        numw = len(labMTvector)

        wordvec = zeros(numw)

        [total,date] = sumfiles(start,end,wordvec,lang,numw)
            
        # write the total into a file for date
        print "printing to {0}".format(date.strftime('%Y-%m-%d'))
        f = open(outfile,'w')
        for i in xrange(numw):
            f.write('{0}\n'.format(total[i]))
        f.close()
        # except:
        #     print "failed on {0}".format(date.strftime('%Y-%m-%d'))
        #     print "-------------------------------"

    if sys.argv[1] == 'list':
        print "heads up, the second word after list needs to be the language"
        labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+region[2]+'.txt',returnVector=True)
        numw = len(labMTvector)

        wordvec = zeros(numw)
        for day in days:
            # this should handle the array object by reference
            [tmp,date] = sumfiles(day,day,wordvec,lang,numw)
            wordvec+=tmp
            
        # write the total into a file for date
        print "printing to {0}".format(outfile)
        f = open(outfile,'w')
        for i in xrange(numw):
            f.write('{0:.0f}\n'.format(wordvec[i]))
        f.close()

def timeseries(option,start,end,region,useStopWindow=True):
    labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+region[2]+'.txt',returnVector=True)
    numw = len(labMTvector)
    if option == "recompute":
        print "opening in write mode"
        g = codecs.open('word-vectors/'+region[0].lower()+'/sumhapps.csv','w','utf8')
        g.write('date,value\n')
        h = codecs.open('word-vectors/'+region[0].lower()+'/sumfreq.csv','w','utf8')
    else:
        print "opening in append mode"        
        g = codecs.open('word-vectors/'+region[0].lower()+'/sumhapps.csv','a','utf8')
        h = codecs.open('word-vectors/'+region[0].lower()+'/sumfreq.csv','a','utf8')
    # loop over time
    currDay = copy.copy(start)
    while currDay <= end:
        # empty array
        happsarray = zeros(24)
        dayhappsarray = zeros(1)
        wordarray = [zeros(numw) for i in xrange(24)]
        daywordarray = zeros(numw)

        print 'reading word-vectors/'+region[0].lower()+'/{0}'.format(currDay.strftime('%Y-%m-%d-sum.csv'))
        try:
            f = codecs.open('word-vectors/'+region[0].lower()+'/{0}-sum.csv'.format(currDay.strftime('%Y-%m-%d')),'r','utf8')
            daywordarray = array(map(float,f.read().split('\n')[0:numw]))
            f.close()
            # print daywordarray
            # print len(daywordarray)
            # compute happiness of the word vectors
            if useStopWindow:
                stoppedVec = stopper(daywordarray,labMTvector,labMTwordList,ignore=["thirsty","pakistan","india","nigga","niggaz","niggas","nigger"])
                happs = emotionV(stoppedVec,labMTvector)
            else:
                happs = emotionV(daywordarray,labMTvector)
            dayhappsarray[0] = happs

    
            # write out the day happs
            print 'writing word-vectors/{1}/{0}'.format(currDay.strftime('%Y-%m-%d-sum.csv'),region[0].lower())
            f = codecs.open('word-vectors/{1}/{0}-sumhapps.csv'.format(currDay.strftime('%Y-%m-%d'),region[0].lower()),'w','utf8')
            f.write('{0},{1}\n'.format(currDay.strftime('%Y-%m-%d'),dayhappsarray[0]))    
            f.close()
    
            g.write('{0},{1}\n'.format(currDay.strftime('%Y-%m-%d'),dayhappsarray[0]))
            h.write('{0},{1:.0f}\n'.format(currDay.strftime('%Y-%m-%d'),sum(dayhappsarray)))
        except:
            print "failed"

        # # compute happiness of the word vectors
        # for i in xrange(24):
        #     stoppedVec = stopper(wordarray[i],labMTvector)
        #     happs = emotionV(stoppedVec,labMTvector)
        #     happsarray[i] = happs
        #     print "happiness of the hour is {0:.3f}".format(happsarray[i])

        # # write out the day happs
        # print "writing keywords/{0}/{1}-happs-{2}.csv".format(folderNames[wordCount],currDay.strftime('%d.%m.%y'),wordCount,)
        # f = codecs.open('keywords/{0}/{1}-happs-{2}.csv'.format(folderNames[wordCount],currDay.strftime('%d.%m.%y'),wordCount,),'w','utf8')
        # for i in xrange(24):
        #     f.write('{0},{1:.3f}'.format(currDay.strftime('%Y-%m-%d'),happsarray[i]))
        # f.close()

        # increase the days
        currDay += datetime.timedelta(days=1)
        
    g.close()
    h.close()

if __name__ == '__main__':

    # do the rsync
    start = datetime.datetime(2015,2,4)
    end = datetime.datetime.now()

    loopdates(start,end)


