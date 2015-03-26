# rest.py
#
# goal here is to expose function for taking two dates and adding the frequency vectors between those dates
#
# USAGE
# python rest.py prevvectors YYYY-mm-dd YYYY-mm-dd language
# python rest.py range YYYY-mm-dd YYYY-mm-dd saveas.csv language
# python rest.py list language YYYY-mm-dd YYYY-mm-dd YYYY-mm-dd YYYY-mm-dd YYYY-mm-dd ... YYYY-mm-dd saveas.csv

import datetime
import numpy
import sys
import copy
from labMTsimple.storyLab import *

def sumfiles(start,end,array,lang,numw):
    curr = copy.copy(start)
    while curr <= end:
        # print "adding {0}".format(curr.strftime('%Y-%m-%d'))
        try:
            f = open('word-vectors/{1}/{0}-sum.csv'.format(curr.strftime('%Y-%m-%d'),lang),'r')
            tmp = f.read().split('\n')
            f.close()
            while len(tmp) > numw:
                del(tmp[-1])
            array=array+numpy.array(map(int,tmp))
        except:
            print "could not load {0}".format(curr.strftime('%Y-%m-%d'))
            print 'could not load word-vectors/{1}/{0}-sum.csv'.format(curr.strftime('%Y-%m-%d'),lang)
            # raise 
        curr+=datetime.timedelta(days=1)

    return array,curr

if __name__ == '__main__':
    if sys.argv[1] == 'prevvectors':
        [year,month,day] = map(int,sys.argv[2].split('-'))
        start = datetime.datetime(year,month,day)
        [year,month,day] = map(int,sys.argv[3].split('-'))
        end = datetime.datetime(year,month,day)
        lang = sys.argv[4]
        labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,lang=lang,returnVector=True)
        numw = len(labMTvector)

        maincurr = copy.copy(start+datetime.timedelta(days=-1))
        while maincurr<end:
            array = numpy.zeros(numw)
            # added the try loop to handle failure inside the sumfiles
            # try:
            [total,date] = sumfiles(maincurr+datetime.timedelta(days=-6),maincurr+datetime.timedelta(days=0),array,lang,numw)
            
            # write the total into a file for date
            print "printing to {0}-prev7.csv".format(date.strftime('%Y-%m-%d'))
            f = open('word-vectors/{1}/{0}-prev7.csv'.format(date.strftime('%Y-%m-%d'),lang),'w')
            for i in xrange(numw):
                f.write('{0:.0f}\n'.format(total[i]))
            f.close()
            # except:
            #     print "failed on {0}".format(date.strftime('%Y-%m-%d'))
            #     print "-------------------------------"
            maincurr+=datetime.timedelta(days=1)

    if sys.argv[1] == 'range':
        [year,month,day] = map(int,sys.argv[2].split('-'))
        start = datetime.datetime(year,month,day)
        [year,month,day] = map(int,sys.argv[3].split('-'))
        end = datetime.datetime(year,month,day)
        outfile = sys.argv[4]
        lang = sys.argv[5]
        labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,lang=lang,returnVector=True)
        numw = len(labMTvector)

        array = numpy.zeros(numw)

        [total,date] = sumfiles(start,end,array,lang,numw)
            
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
        lang = sys.argv[2]
        labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,lang=lang,returnVector=True)
        numw = len(labMTvector)
        days = []
        # note that [1:] is one longer than needed, but xrange won't hit it
        for i in xrange(3,len(sys.argv[2:])):
            [year,month,day] = map(int,sys.argv[i].split('-'))
            days.append(datetime.datetime(year,month,day))
        print days

        outfile = sys.argv[-1]
        print outfile
        array = numpy.zeros(numw)
        for day in days:
            # this should handle the array object by reference
            [tmp,date] = sumfiles(day,day,array,lang,numw)
            array+=tmp
            
        # write the total into a file for date
        print "printing to {0}".format(outfile)
        f = open(outfile,'w')
        for i in xrange(numw):
            f.write('{0:.0f}\n'.format(array[i]))
        f.close()








