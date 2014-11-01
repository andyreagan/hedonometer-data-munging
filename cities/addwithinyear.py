# add up all the word vectors in a year
#
# USAGE
#
# python addwithinyear.py 

import sys
import codecs
import os
# ahh
from numpy import *

def process(fname,index):
  rawfile = fname
  newfile = rawfile+".new"
  
  f = open(rawfile,'r')
  oldindices = f.read().split(',')
  f.close()
  # print len(oldindices)

  newvec = [oldindices[i] if i > -1 else 0 for i in index]
  # print len(newvec)

  f = open(newfile,'w')
  f.write('{0}'.format(newvec[0]))


if __name__ == "__main__":

  print "yay"


  for year in ['2011','2012','2013']:
    total = zeros(10222)
    for root, dirs, files in os.walk('word-vectors/'+year):
      for fname in files:
        if fname.endswith('.csv.new'):
          print fname
          f = open('word-vectors/'+year+'/'+fname,'r')
          indices = map(int,f.read().split(','))
          f.close()
          total=total+array(indices)

    f = open('word-vectors/'+year+'/US.csv',"w")
    f.write('{0:.0f}'.format(total[0]))
    for i in xrange(1,10222):
      f.write(',{0:.0f}'.format(total[i]))
    f.close()        
    f = open('word-vectors/'+year+'/US.csv.new',"w")
    f.write('{0:.0f}'.format(total[0]))
    for i in xrange(1,10222):
      f.write(',{0:.0f}'.format(total[i]))
    f.close()        

  year = '2014'
  total = zeros(10222)
  for root, dirs, files in os.walk('word-vectors/'+year):
    for fname in files:
      if fname.endswith('.csv'):
        print fname
        f = open('word-vectors/'+year+'/'+fname,'r')
        indices = map(int,f.read().split(','))
        f.close()
        total=total+array(indices)

  f = open('word-vectors/'+year+'/US.csv',"w")
  f.write('{0:.0f}'.format(total[0]))
  for i in xrange(1,10222):
    f.write(',{0:.0f}'.format(total[i]))
  f.close()        
