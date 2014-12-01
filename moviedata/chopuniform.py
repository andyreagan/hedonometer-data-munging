# chop.py
#
# chop up a text into a bunch of frequency vectors of length
# 
# USAGE
#
# python chop.py data/count-of-monte-cristo.txt output french

import codecs # handle utf8
import re
from labMTsimple.storyLab import *
import sys, os
sys.path.append('/usr/share/nginx/wiki/mysite/mysite')
sys.path.append('/usr/share/nginx/wiki/mysite')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from math import floor

from hedonometer.models import Book

def chopper(words,labMT,labMTvector,outfile,minSize=10000,numPoints=100):
    print "now splitting the text into chunks of size 10000"
    # print "and printing those frequency vectors"

    # initialize timeseries, only thing we're after
    timeseries = [0 for i in xrange(numPoints)]

    # how much to jump
    from numpy import floor
    step = int(floor((len(words)-minSize)/(numPoints-1)))
    print "there are "+str(len(words))+" words in the book"
    print "step size "+str(step)

    # do it 99 times
    for i in xrange(numPoints-1):
      chunk = unicode(' ').join(words[(i*step):(minSize+i*step)])
      textValence,textFvec = emotion(chunk,labMT,shift=True,happsList=labMTvector)
      stoppedVec = stopper(textFvec,labMTvector,labMTwordList,stopVal=2.0)
      timeseries[i] = emotionV(stoppedVec,labMTvector)
    # final chunk
    i = numPoints-1
    # only difference: go to the end
    # may be 10-100 more words there (we used floor on the step)
    chunk = unicode(' ').join(words[(i*step):])
    textValence,textFvec = emotion(chunk,labMT,shift=True,happsList=labMTvector)
    stoppedVec = stopper(textFvec,labMTvector,labMTwordList,stopVal=2.0)
    timeseries[i] = emotionV(stoppedVec,labMTvector)

    g = open(outfile,"w")
    g.write("{0:.5f}".format(timeseries[0]))
    for i in xrange(1,numPoints):
        g.write(",")
        g.write("{0:.5f}".format(timeseries[i]))
    g.write("\n")
  
if __name__ == "__main__":
    # rawbook,saveas,lang = sys.argv[1:]
    # f = open("testbooks.txt","r")
    f = open("gutenberg/diskBooksData.txt","r")
    # h = codecs.open("analysis-log.csv","w","utf8")
    h = open("analysis-log.csv","w")
    f.readline()
    count = 0
    for line in f:
        print "-"*80
  
        tmp = line.rstrip().split("\t")
        print "reading:"
        print tmp
        
        # check that we got a language out
        if len(tmp) > 3:
            lang = tmp[3].lower()
        else:
            lang = "unknown"
  
        # we'll capture this one
        if lang == "en":
           lang = "english"
    
        # check if we have the language
        if lang in ["arabic","chinese","english","french","german","hindi","indonesian","korean","pashto","portuguese","russian","spanish","urdu"]:
          
            saveas = "timeseries/"+tmp[0]+".csv"
            count+=1
            labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+lang+'.txt',returnVector=True)
            g = codecs.open("gutenberg/books/"+tmp[0]+".txt","r","utf8")
            raw_text = g.read()
            g.close()
              
            words = [x.lower() for x in re.findall(r"[\w\@\#\'\&\]\*\-\/\[\=\;]+",raw_text,flags=re.UNICODE)]
              
            # avhapps = emotion(raw_text,labMT)
  
            if len(words) > 50000:
              chopper(words,labMT,labMTvector,saveas)
              h.write("{0},{1},{2},{3}".format(tmp[0],tmp[1],tmp[2],lang))
              h.write("\n")
              
            # b = Book(filename=tmp[0],title=tmp[1],author=tmp[2],language=lang,happs=avhapps,length=len(words))
            # b.save()
        
    print "read a total of " + str(count) + " books"
    f.close()
    h.close()



