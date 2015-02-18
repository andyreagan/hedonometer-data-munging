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

from hedonometer.models import NYT

sections = ['arts','books','classified','cultural','editorial','education','financial','foreign','home','leisure','living','magazine','metropolitan','movies','national','regional','science','society','sports','style','television','travel','weekend','week_in_review',]

def addToModel():
  for sec in sections:
    n = NYT(genre=sec,language="english",filename="NYT_labVec_"+sec+".csv",happs=0.0,variance=0.0,ignorewords="")
    n.save()
  sec="all"
  n = NYT(genre=sec,language="english",filename="NYT_labVec_"+sec+".csv",happs=0.0,variance=0.0,ignorewords="")
  n.save()

def process():
  query = NYT.objects.all()

  for movie in query:

    filename = movie.filename # .replace(" ","-")
    # print filename
    if filename[0:4] == "The-":
      # print "starts with the"
      correctname = filename
      filename = filename[4:]+",-The"
      try:
        shutil.copyfile("/usr/share/nginx/data/moviedata/rawer/"+filename+".html.end.beg","/usr/share/nginx/data/moviedata/rawer/"+correctname+".html.end.beg")
      except:
        print filename+" rawer .end.beg failed, copy manually"
      try:
        shutil.copyfile("/usr/share/nginx/data/moviedata/raw/"+filename+".txt","/usr/share/nginx/data/moviedata/raw/"+correctname+".txt")
      except:
        print filename+" raw failed, copy manually"
      try:
        shutil.copyfile("/usr/share/nginx/data/moviedata/rawer/"+filename+".html.clean01","/usr/share/nginx/data/moviedata/rawer/"+correctname+".html.clean01")
      except:
        print filename+" rawer clean01 failed, copy manually"


  
if __name__ == "__main__":
  # assume everything is in english
  lang = "english"
  labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+lang+'.txt',returnVector=True)

  addToModel()

  query = NYT.objects.all()
  for section in query:
    print section




