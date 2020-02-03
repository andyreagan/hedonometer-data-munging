# take the hourly-frequency and word vectors
# sum them to day level
# compute happiness at hour level, day level
# for all keywords
#
# USAGE:
# python timeseries.py 2014-01-01 2014-06-26

import codecs
import copy
import datetime
import re
import sys

import numpy as np
from labMTsimple.storyLab import *

if __name__ == '__main__':
    [year, month, day] = map(int, sys.argv[1].split('-'))
    start = datetime.datetime(year, month, day)

    [year, month, day] = map(int, sys.argv[2].split('-'))
    end = datetime.datetime(year, month, day)

    goal = sys.argv[3]

    lang = "english"
    labMT, labMTvector, labMTwordList = emotionFileReader(
        stopval=0.0, lang=lang, returnVector=True)

    print labMTvector
    print len(labMTvector)

    scorelistf = sys.argv[4]
    f = open(scorelistf, 'r')
    scorelist = [float(line.rstrip()) for line in f]
    f.close()

    outfile = sys.argv[5]

    print scorelist
    print len(scorelist)

    if goal == "recompute":
        print "opening in write mode"
        g = codecs.open('word-vectors/'+outfile+'.csv', 'w', 'utf8')
        g.write('date,value\n')
        # h = codecs.open('word-vectors/sumfreq.csv','w','utf8')
    else:
        print "opening in append mode"
        g = codecs.open('word-vectors/'+outfile+'.csv', 'a', 'utf8')
        # h = codecs.open('word-vectors/sumfreq.csv','a','utf8')
    # loop over time
    currDay = copy.copy(start)
    while currDay <= end:
        # empty array
        happsarray = np.zeros(24)
        dayhappsarray = np.zeros(1)
        wordarray = [np.zeros(10222) for i in xrange(24)]
        daywordarray = np.zeros(10222)

        print 'reading word-vectors/{0}'.format(
            currDay.strftime('%Y-%m-%d-sum.csv'))
        try:
            f = codecs.open(
                'word-vectors/{0}-sum.csv'.format(currDay.strftime('%Y-%m-%d')), 'r', 'utf8')
            daywordarray = np.array(map(float, f.read().split('\n')[0:10222]))
            f.close()
            # print daywordarray
            # print len(daywordarray)
            # compute happiness of the word vectors
            stoppedVec = stopper(daywordarray, scorelist, labMTwordList, ignore=[
                                 "thirsty", "pakistan", "india", "nigga", "niggaz", "niggas", "nigger"])
            happs = emotionV(stoppedVec, scorelist)
            print happs
            dayhappsarray[0] = happs

            # write out the day happs
            print 'writing ' + \
                'word-vectors/{0}-'.format(currDay.strftime('%Y-%m-%d')
                                           )+outfile+'.csv'
            f = codecs.open(
                'word-vectors/{0}-'.format(currDay.strftime('%Y-%m-%d'))+outfile+'.csv', 'w', 'utf8')
            f.write('{0},{1}\n'.format(
                currDay.strftime('%Y-%m-%d'), dayhappsarray[0]))
            f.close()

            g.write('{0},{1}\n'.format(
                currDay.strftime('%Y-%m-%d'), dayhappsarray[0]))
            # h.write('{0},{1:.0f}\n'.format(currDay.strftime('%Y-%m-%d'),sum(stoppedVec)))
        except:
            print "Unexpected error:", sys.exc_info()[0]
            print "failed"
            # raise

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
