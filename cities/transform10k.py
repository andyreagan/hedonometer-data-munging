# move from the 9976 list to the 10222 list
# i accidentally deleted the writeindexfile function
# but we can still read it
# this is based off of the process10k a directory up
#
# USAGE
#
# python transform10k.py 

import sys
import codecs
import os
import re

def readindexfile(fname):
  f = open(fname,'r')
  tmp = f.read().split('\n')[:-1]
  print len(tmp)
  index = map(int,tmp)
  f.close()

  return index

def process(fname,index):
  rawfile = fname
  newfile = re.sub('--','-',rawfile+'.new')
  
  f = open(rawfile,'r')
  oldindices = f.read().split(',')
  f.close()
  # print len(oldindices)

  newvec = [oldindices[i] if i > -1 else 0 for i in index]
  # print len(newvec)

  f = open(newfile,'w')
  f.write('{0}'.format(newvec[0]))
  for i in xrange(1,10222):
    f.write(',{0}'.format(newvec[i]))
  f.close()

if __name__ == "__main__":

  print "yay"

  index = readindexfile("index.csv")

  for root, dirs, files in os.walk("word-vectors/2011_PLOS"):
    for fname in files:
      if fname.endswith('.csv'):
        print fname
        process("word-vectors/2011_PLOS/"+fname,index)
