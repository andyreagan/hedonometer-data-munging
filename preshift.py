# pre compute shifts for each day against the previous seven
# only need to save the top 10 words
# save it in a csv

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

    lang = sys.argv[3]
    #lang = "english"

    labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+lang+'.txt',returnVector=True)
    numw = len(labMTvector)

    # g = codecs.open('word-vectors/sumhapps.csv','w','utf8')
   
    # loop over time
    currDay = copy.copy(start)
    while currDay <= end:
        # empty array
        wordarray = np.zeros(numw)
        prevwordarray = np.zeros(numw)

        print 'reading word-vectors/{1}/{0}'.format(currDay.strftime('%Y-%m-%d-sum.csv'),lang)
        try:
            f = codecs.open('word-vectors/{1}/{0}-sum.csv'.format(currDay.strftime('%Y-%m-%d'),lang),'r','utf8')
            wordarray = np.array(map(float,f.read().split('\n')[0:numw]))
            f.close()
            print 'reading word-vectors/{1}/{0}'.format(currDay.strftime('%Y-%m-%d-prev7.csv'),lang)
            f = codecs.open('word-vectors/{1}/{0}-prev7.csv'.format(currDay.strftime('%Y-%m-%d'),lang),'r','utf8')
            prevwordarray = np.array(map(float,f.read().split('\n')[0:numw]))
            f.close()
            # print daywordarray
            print len(wordarray)
            print len(prevwordarray)
            # compute happiness of the word vectors
            wordarrayst = stopper(wordarray,labMTvector,labMTwordList,ignore=["thirsty","pakistan","india","nigga","niggas","niggaz","nigger"])
            prevwordarrayst = stopper(prevwordarray,labMTvector,labMTwordList,ignore=["thirsty","pakistan","india","nigga","niggas","niggaz","nigger"])

            happs = emotionV(wordarrayst,labMTvector)
            prevhapps = emotionV(prevwordarrayst,labMTvector)
            # print happs

            [sortedMag,sortedWords,sortedType,sumTypes] = shift(prevwordarrayst,wordarrayst,labMTvector,labMTwordList)
            # print sortedMag[:10]
            # print sortedWords[:10]
            # print sortedType[:10]
            # print sumTypes
            print 'writing shifts/{1}/{0}-shift.csv'.format(currDay.strftime('%Y-%m-%d'),lang)
            g = codecs.open('shifts/{1}/{0}-shift.csv'.format(currDay.strftime('%Y-%m-%d'),lang),'w','utf8')
            g.write("mag,word,type")
            for i in xrange(10):
                g.write("\n")
                g.write(str(sortedMag[i]))
                g.write(",")
                g.write(sortedWords[i])
                g.write(",")
                g.write(str(sortedType[i]))
            g.close()
            print 'writing shifts/{1}/{0}-metashift.csv'.format(currDay.strftime('%Y-%m-%d'),lang)
            g = open('shifts/{1}/{0}-metashift.csv'.format(currDay.strftime('%Y-%m-%d'),lang),'w')
            g.write("refH,compH,negdown,negup,posdown,posup")
            g.write("\n{0},{1},{2},{3},{4},{5}".format(prevhapps,happs,sumTypes[0],sumTypes[1],sumTypes[2],sumTypes[3]))
            g.close()
            # write out the shift
            
        except:
            print "failed"
            raise

        # increase the days
        currDay += datetime.timedelta(days=1)
        
    




