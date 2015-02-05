# take the hourly-frequency and word vectors
# sum them to day level
# compute happiness at hour level, day level
# for all keywords
#
# USAGE: 
# python timeseries.py append 2014-01-01 2014-06-26 english

import codecs
from labMTsimple.storyLab import *
import datetime
import copy
import numpy as np
import sys
import re

if __name__ == '__main__':
    [year,month,day] = map(int,sys.argv[1].split('-'))
    start = datetime.datetime(year,month,day)

    [year,month,day] = map(int,sys.argv[2].split('-'))
    end = datetime.datetime(year,month,day)

    goal = sys.argv[3]

    lang = sys.argv[4]
    # lang = "english"

    useStopWindow = True
    if len(sys.argv) > 5:
        if sys.argv[5] in ["false","False","0"]:
            useStopWindow = False
            print "not using a stop window"

    labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+lang+'.txt',returnVector=True)
    numw = len(labMTvector)
    if goal == "recompute":
        print "opening in write mode"
        g = codecs.open('word-vectors/'+lang+'/sumhapps.csv','w','utf8')
        g.write('date,value\n')
        h = codecs.open('word-vectors/'+lang+'/sumfreq.csv','w','utf8')
    else:
        print "opening in append mode"        
        g = codecs.open('word-vectors/'+lang+'/sumhapps.csv','a','utf8')
        h = codecs.open('word-vectors/'+lang+'/sumfreq.csv','a','utf8')
    # loop over time
    currDay = copy.copy(start)
    while currDay <= end:
        # empty array
        happsarray = np.zeros(24)
        dayhappsarray = np.zeros(1)
        wordarray = [np.zeros(numw) for i in xrange(24)]
        daywordarray = np.zeros(numw)

        print 'reading word-vectors/'+lang+'/{0}'.format(currDay.strftime('%Y-%m-%d-sum.csv'))
        try:
            f = codecs.open('word-vectors/'+lang+'/{0}-sum.csv'.format(currDay.strftime('%Y-%m-%d')),'r','utf8')
            daywordarray = np.array(map(float,f.read().split('\n')[0:numw]))
            f.close()
            # print daywordarray
            # print len(daywordarray)
            # compute happiness of the word vectors
            if useStopWindow:
                stoppedVec = stopper(daywordarray,labMTvector,labMTwordList,ignore=["lynch","thirsty","pakistan","india","nigga","niggaz","niggas","nigger"])
                happs = emotionV(stoppedVec,labMTvector)
            else:
                happs = emotionV(daywordarray,labMTvector)
            dayhappsarray[0] = happs

    
            # write out the day happs
            print 'writing word-vectors/{1}/{0}'.format(currDay.strftime('%Y-%m-%d-sum.csv'),lang)
            f = codecs.open('word-vectors/{1}/{0}-sumhapps.csv'.format(currDay.strftime('%Y-%m-%d'),lang),'w','utf8')
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




