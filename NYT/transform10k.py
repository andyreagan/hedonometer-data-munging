# convert 50K word vectors in 10222 word vectors (the ones we have scores for)
#
# USAGE
#
# python transform10k.py 

import sys
import codecs
import os

sys.path.append('/home/prod/hedonometer')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','mysite.settings')
from django.conf import settings

from hedonometer.models import NYT

def writeindexfile(name,lang = "english"):
  f = codecs.open("../labMT/labMTwords-"+lang+".csv","r","utf8")
  tmp = f.read()
  f.close()

  lines = tmp.split("\n")
  # print len(lines)
  # print lines[0:10]
  # print lines[10220:10230]
  words = lines
  # del(lines[-1])

  # load in the longer version
  f = codecs.open("NYT_labVecs/wordVec.csv","r","utf8")
  tmp = f.read()
  f.close()

  longerlines = tmp.split("\n")
  # print len(longerlines)
  # print longerlines[0:10]
  # print longerlines[49990:50020]
  # longerwords = [x.split(u'\n')[0].rstrip() for x in longerlines]
  longerwords = longerlines

  # print len(longerwords)
  # print longerwords[0:10]
  # print longerwords[49990:50020]

  # fast search
  missed = 0
  for word in words:
    if word not in longerwords:
      missed += 1
      # print word
    
  print "missed {0}".format(missed)

  # slow search
  missed = 0
  index = [0 for x in xrange(len(words))]
  for i in xrange(len(words)):
    found = False
    for j in xrange(len(longerwords)):
      if words[i] == longerwords[j]:
        found = True
        index[i] = j
        break
    if not found:
      missed += 1
      index[i] = -1
      # print words[i]
        
  print "missed {0}".format(missed)
  # print index
  f = codecs.open(name,"w")
  f.write('{0:.0f}'.format(index[0]))
  for i in xrange(1,len(index)):
    f.write('\n{0:.0f}'.format(index[i]))
  f.close()

def readindexfile(name):
  f = codecs.open(name,"r","utf8")
  tmp = f.read().split("\n")
  f.close()

  return map(int,tmp)

def process(inf,outf,index):
  print "reading in input file..."
  f = codecs.open(inf,"r","utf8")
  tmp = [int(line.rstrip()) for line in f]
  f.close()

  # could make it of size max(index)+1...
  vec10k = [0 for i in xrange(10222)]

  print "transforming..."
  for j in xrange(10222):
    if index[j] > -1:
      vec10k[j] = tmp[index[j]]
    else:
      vec10k[j] = 0.0

  print "writing new file..."
  f = codecs.open(outf,"w")
  f.write('{0:.0f}'.format(vec10k[0]))
  for i in xrange(1,len(vec10k)):
    f.write('\n{0:.0f}'.format(vec10k[i]))
  f.close()

def processNYT(index):
  query = NYT.objects.all()
  for q in query:
    process("NYT_labVecs/"+q.filename+".stripped","NYT_labVecs/"+q.filename+".stripped.indexed",index)

if __name__ == "__main__":
  # writeindexfile("indexer.csv")
  
  index = readindexfile("indexer.csv")
  print len(index)

  # inf = sys.argv[1]
  # outf = sys.argv[2]
  # process(inf,outf,index)

  processNYT(index)
  






