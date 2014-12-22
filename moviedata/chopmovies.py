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
from numpy import floor
import sys, os
sys.path.append('/home/prod/hedonometer')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','mysite.settings')
from django.conf import settings

from hedonometer.models import Movie

def chopper(words,labMT,labMTvector,outfile,minSize=1000):
  # print "now splitting the text into chunks of size 1000"
  # print "and printing those frequency vectors"
  allFvec = []
  for i in xrange(int(floor(len(words)/minSize))):
    chunk = unicode('')
    if i == int(floor(len(words)/minSize))-1:
      # take the rest
      # print 'last chunk'
      # print 'getting words ' + str(i*minSize) + ' through ' + str(len(words)-1)
      for j in xrange(i*minSize,len(words)-1):
        chunk += words[j]+unicode(' ')
    else:
      # print 'getting words ' + str(i*minSize) + ' through ' + str((i+1)*minSize)
      for j in xrange(i*minSize,(i+1)*minSize):
        chunk += words[j]+unicode(' ')
        # print chunk[0:10]
    textValence,textFvec = emotion(chunk,labMT,shift=True,happsList=labMTvector)
      # print chunk
    # print 'the valence of {0} part {1} is {2}'.format(rawbook,i,textValence)
        
    allFvec.append(textFvec)


  f = open(outfile,"w")
  if len(allFvec) > 0:
    # print "writing out the file to {0}".format(outfile) 
    f.write('{0:.0f}'.format(allFvec[0][0]))
    for k in xrange(1,len(allFvec)):
      f.write(',{0:.0f}'.format(allFvec[k][0]))
    for i in xrange(1,len(allFvec[0])):
      f.write("\n")
      f.write('{0:.0f}'.format(allFvec[0][i]))
      for k in xrange(1,len(allFvec)):
        f.write(',{0:.0f}'.format(allFvec[k][i]))
    f.close()
  else:
    print "\""*40
    print "could not write to {0}".format(outfile)
    print "\""*40
  # print "done!"

def precomputeTimeseries(fullVec,labMT,labMTvector,outfile):
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

import shutil
  
if __name__ == "__main__":
  # assume everything is in english
  lang = "english"
  labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+lang+'.txt',returnVector=True)

  # windowSizes = [500,1000,2000,5000,10000]
  windowSizes = [2000]

  u = open("faillog.txt","a")

  query = Movie.objects.all()
  # query = Movie.objects.filter(title="127 Hours")
  for movie in query[934:]:

    filename = movie.filename # .replace(" ","-")
    # print filename
    if filename[0:4] == "The-":
      # print "starts with the"
      correctname = filename
      filename = filename[4:]+",-The"
      shutil.copyfile("/usr/share/nginx/data/moviedata/rawer/"+filename+".html.clean01","/usr/share/nginx/data/moviedata/rawer/"+correctname+".txt")

    print "filename:"
    print filename

    if os.path.isfile("/usr/share/nginx/data/moviedata/raw/"+filename+".txt"):
      print "title:"
      print movie.title
      print "opening raw/"+filename+".txt"
      f = codecs.open("raw/"+filename+".txt","r","utf8")
      raw_text_clean = f.read()
      f.close()
      print "opening rawer/"+filename+".html.clean04"
      # f = codecs("rawer/"+filename+".html.clean04","r")
      try:
        f = codecs.open("rawer/"+filename+".html.clean04","r","utf8")
        raw_text = f.read()
      except UnicodeDecodeError:
        u.write(movie.title)
        u.write("\n")
        u.write("UnicodeDecodeError")
        u.write("\n")
      except IOError:
        u.write(movie.title)
        u.write("\n")
        u.write("IOError")
        u.write("\n")
      except:
        u.write(movie.title)
        u.write("\n")
        u.write("unknown error")
        u.write("\n")
        u.close()
        raise
      f.close()
    
      words = [x.lower() for x in re.findall(r"[\w\@\#\'\&\]\*\-\/\[\=\;]+",raw_text_clean,flags=re.UNICODE)]
      lines = raw_text.split("\n")
      kwords = []
      klines = []
      for i in xrange(len(lines)):
        if lines[i][0:3] != "<b>":
          tmpwords = [x.lower() for x in re.findall(r"[\w\@\#\'\&\]\*\-\/\[\=\;]+",lines[i],flags=re.UNICODE)]
          kwords.extend(tmpwords)
          klines.extend([i for j in xrange(len(tmpwords))])
          
      # avhapps = emotion(raw_text,labMT)
      print "length of the original parse"
      print len(words)
      print "length of the new parse"
      print len(kwords)
      # print len(klines)
      # print klines[0:20]

      for window in windowSizes:
        print window

        # print klines[0:(window/10)]
        breaks = [klines[window/10*i] for i in xrange(int(floor(float(len(klines))/window*10)))]
        breaks[0] = 0
        # print [window/10*i for i in xrange(int(floor(float(len(klines))/window*10)))]
        # print breaks
        # print len(breaks)
        f = open("word-vectors/"+str(window)+"/"+movie.filename+"-breaks.csv","w")
        f.write(",".join(map(str,breaks)))
        f.close()
        chopper(kwords,labMT,labMTvector,"word-vectors/"+str(window)+"/"+movie.filename+".csv",minSize=window/10)

        f = open("word-vectors/"+str(window)+"/"+movie.filename+".csv","r")
        fullVec = [map(int,line.split(",")) for line in f]
        f.close()
  
        # some movies are blank
        if len(fullVec) > 0:
          if len(fullVec[0]) > 9:
            precomputeTimeseries(fullVec,labMT,labMTvector,"timeseries/"+str(window)+"/"+movie.filename+".csv")
        else:
          print "this movie is blank:"
          print movie.title

    else:
      print "movie does not have a file at:"
      print "/usr/share/nginx/data/moviedata/raw/"+filename+".txt"
      u.write(movie.title)
      u.write("\n")
      u.write("missing file at ")
      u.write("/usr/share/nginx/data/moviedata/raw/"+filename+".txt")
      u.write("\n")
      
  u.close()

