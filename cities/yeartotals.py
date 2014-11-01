# add up all the word vectors in a year
#
# USAGE
#
# python addwithinyear.py 

import sys
import codecs
import os

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


  year = '2014'
  total = []
  for root, dirs, files in os.walk('word-vectors/'+year):
    for fname in files:
      if fname.endswith('.csv'):
        print fname[:-4]
        f = open('word-vectors/'+year+'/'+fname,'r')
        indices = map(int,f.read().split(','))
        f.close()
        total.append([fname[:-4],sum(indices)])

  f = open('totals'+year+'.csv',"w")
  i = 0
  f.write('{1:.0f},{0}'.format(total[i][0],total[i][1]))
  for i in xrange(1,len(total)):
    f.write('\n{1:.0f},{0}'.format(total[i][0],total[i][1]))
  f.close()

  total.sort(key=lambda x: x[1])

  f = open('totals'+year+'sorted.csv',"w")
  i = 0
  f.write('{1:.0f},{0}'.format(total[i][0],total[i][1]))
  for i in xrange(1,len(total)):
    f.write('\n{1:.0f},{0}'.format(total[i][0],total[i][1]))
  f.close()        
