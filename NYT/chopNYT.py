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
from numpy import floor,array,zeros
import sys, os
sys.path.append('/home/prod/hedonometer')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','mysite.settings')
from django.conf import settings

from hedonometer.models import NYT

sections = ['arts','books','classified','cultural','editorial','education','financial','foreign','home','leisure','living','magazine','metropolitan','movies','national','regional','science','society','sports','style','television','travel','weekend','week_in_review',]

def addToModel():
  for sec in sections:
    n = NYT(genre=sec,language="english",filename="NYT_labVec_"+sec+".csv",happs=0.0,variance=0.0,ignorewords="")
    n.save()
  sec="all"
  n = NYT(genre=sec,language="english",filename="NYT_labVec_"+sec+".csv",happs=0.0,variance=0.0,ignorewords="")
  n.save()

def makeAllFile():
  total = zeros(10222)
  for q in NYT.objects.all():
    print q.genre
    # build up a big word vec
    if not q.genre == 'all':
      f = open("NYT_labVecs/"+q.filename,"r")
      f.readline()
      vec = [int(line.split(",")[1].rstrip()) for line in f]
      f.close()
      f = open("NYT_labVecs/"+q.filename+".stripped","w")
      f.write('{0:.0f}'.format(vec[0]))
      for v in vec[1:]:
        f.write('\n{0:.0f}'.format(v))
      f.close()
      total += array(vec)
  f = open("NYT_labVecs/"+"NYT_labVec_all.csv"+".stripped","w")
  f.write('{0:.0f}'.format(total[0]))
  for v in total[1:]:
    f.write('\n{0:.0f}'.format(v))
  f.close()

def process():
  query = NYT.objects.all()
  for section in query:
    pass
  
if __name__ == "__main__":
  # assume everything is in english
  lang = "english"
  labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+lang+'.txt',returnVector=True)

  # addToModel()

  makeAllFile()


