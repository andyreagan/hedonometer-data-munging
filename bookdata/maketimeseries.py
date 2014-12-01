# maketimeseries.py
#
# take the word vectors and make a happiness timeseries
# 
# USAGE
#
# python maketimeseries.py word-vectors/harry8.csv timeseries/harry8.csv

from labMTsimple.storyLab import stopper,emotionV,emotionFileReader
import sys, os
sys.path.append('/home/prod/hedonometer')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
from django.conf import settings

from hedonometer.models import Book

def chopper(fullVec,labMT,labMTvector,outfile):
    minWindows = 10
    timeseries = [0 for i in xrange(len(fullVec[0])+1)]
    # print len(timeseries)

    textFvec = [0 for j in xrange(len(fullVec))]
    for i in xrange(0,minWindows/2):
        textFvec = [textFvec[j]+fullVec[j][i] for j in xrange(len(fullVec))]
        # print "adding point {0}".format(i)

    for i in xrange(minWindows/2,minWindows):
        # print "scoring"
        stoppedVec = stopper(textFvec,labMTvector,labMTwordList,stopVal=2.0)
        timeseries[i-minWindows/2] = emotionV(stoppedVec,labMTvector)
        # print "adding point {0}".format(i)
        textFvec = [textFvec[j]+fullVec[j][i] for j in xrange(len(fullVec))]

    for i in xrange(minWindows,len(timeseries)-1):
        # print "scoring"
        stoppedVec = stopper(textFvec,labMTvector,labMTwordList,stopVal=2.0)
        timeseries[i-minWindows/2] = emotionV(stoppedVec,labMTvector)
        # print "adding point {0}".format(i)
        # print "removing point {0}".format(i-minWindows)
        textFvec = [textFvec[j]+fullVec[j][i]-fullVec[j][i-minWindows] for j in xrange(len(fullVec))]

    for i in xrange(len(timeseries)-1,len(timeseries)+minWindows/2):
        # print "scoring"
        stoppedVec = stopper(textFvec,labMTvector,labMTwordList,stopVal=2.0)
        timeseries[i-minWindows/2] = emotionV(stoppedVec,labMTvector)
        # print "removing point {0}".format(i-minWindows)
        textFvec = [textFvec[j]-fullVec[j][i-minWindows] for j in xrange(len(fullVec))]
    
    # print "done"

    # print timeseries[0:11]
    # print timeseries[-11:]

    g = open(outfile,"w")
    g.write("{0}".format(timeseries[0]))
    for i in xrange(1,len(timeseries)):
        g.write(",")
        # g.write("{0:.5f}".format(timeseries[i]))
        g.write("{0}".format(timeseries[i]))
    g.write("\n")
    g.close()
  
if __name__ == "__main__":
    inf = sys.argv[1]

    b = Book.objects.filter(filename__exact=inf.split(".")[0])
    if len(b) > 0:
        lang = b[0].language
        labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+lang+'.txt',returnVector=True)

        f = open("word-vectors/"+inf,"r")
        fullVec = [map(int,line.split(",")) for line in f]
        f.close()

        print "processing "+b[0].title
        chopper(fullVec,labMT,labMTvector,"timeseries/"+inf)
        print "done"
    else:
        print "could not find book for file "+inf




