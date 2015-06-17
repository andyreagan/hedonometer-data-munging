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
from numpy import floor,zeros,array
import sys, os
sys.path.append('/home/prod/hedonometer')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','mysite.settings')
from django.conf import settings

from hedonometer.models import Actor,Director,Writer,Movie
import shutil
import subprocess
import unirest
import datetime

from labMTsimple.speedy import *
labMTsenti = sentiDict('LabMT',stopVal=0.0)

# assume everything is in english
lang = "english"
labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,lang=lang,returnVector=True)

def loop():
    f = open("titles-clean.txt","r")
    titles = [line.rstrip() for line in f]
    f.close()
    f = open("titles-raw.txt","r")
    rawtitles = [line.rstrip() for line in f]
    f.close()

    startat = 1083
    endat = 1100
    
    for i in xrange(startat,endat):
        title = titles[i]
        rawtitle = rawtitles[i]
        scrape(title,rawtitle,g)

    f.close()

def scrape(title,rawtitle):
    print "-"*80
    print "-"*80
    print title
    print "-"*80

    response = unirest.post("https://imdb.p.mashape.com/movie",
                            headers={
                                # "X-Mashape-Key": "KZE1CO4Mn7mshjabQzICrvp0grcSp1P4tgfjsnMW4yBZK1vhU7",
                                "X-Mashape-Key": "KZE1CO4Mn7mshjabQzICrvp0grcSp1P4tgfjsnMW4yBZK1vhU7",
                                "Content-Type": "application/x-www-form-urlencoded",
                            },
                                params={
                                    "searchTerm": title,
                                })

    print response.body

    if response.body["success"] in [True,"true","True"]:
        print response.body["result"]

        print "-"*80
        print "actors:"
        # go get, or create, all the actor models
        actor_list = []
        for actor in response.body["result"]["cast"]:
            name = actor["actor"]
            print name
            q = Actor.objects.filter(name__exact=name)
            if len(q) > 0:
                a = q[0]
            else:
                a = Actor(name=name)
                a.save()

            actor_list.append(a)

        print "-"*80
        print "directors:"
        director_list = []
        if isinstance(response.body["result"]["director"], basestring):
            directors = [response.body["result"]["director"]]
        else:
            directors = response.body["result"]["director"]
        for director in directors:
            name = director
            print name
            q = Director.objects.filter(name__exact=name)
            if len(q) > 0:
                a = q[0]
            else:
                a = Director(name=name)
                a.save()

            director_list.append(a)

        print "-"*80
        print "writers:"
        writer_list = []
        if isinstance(response.body["result"]["writer"], basestring):
            writers = [response.body["result"]["writer"]]
        else:
            writers = response.body["result"]["writer"]
        for writer in writers:
            name = writer
            print name
            q = Writer.objects.filter(name__exact=name)
            if len(q) > 0:
                a = q[0]
            else:
                a = Writer(name=name)
                a.save()
            writer_list.append(a)
                
        genre = ",".join(response.body["result"].get("genre","none"))
        keywords = ",".join(response.body["result"].get("keywords","none"))
        language = response.body["result"].get("language","none")
        imdbid = response.body["result"].get("id","none")
        metascore = response.body["result"]["metascore"].get("given","none")
        image = response.body["result"].get("poster","none")
        rating = response.body["result"]["rating"].get("content","none")
        date1 = response.body["result"].get("releaseDate","Thu Nov 20 2014")
        if date1 == "Invalid Date":
            date1 = "Thu Nov 20 2014"
        releaseDate = datetime.datetime.strptime(date1,"%a %b %d %Y") # Fri Nov 21 2008
        reviews = response.body["result"]["reviews"].get("user","none")
        runtime = response.body["result"].get("runtime","none")
        storyline = response.body["result"].get("storyline","none")
        year = response.body["result"].get("year","none")

        m = Movie(
            filename = title.replace(" ","-"),
            title = title,
            titleraw = rawtitle,
            # director = director_list,
            # actor = actor_list,
            # writer = writer_list,
            language = language,
            happs = 0.0,
            length = "0",
            ignorewords = "nigg",
            wiki = "nolink",
            image = image,
            genre = genre,
            imdbid = imdbid,
            keywords = keywords,
            metascore = metascore,
            rating = rating,
            releaseDate = releaseDate,
            reviews = reviews,
            runtime = runtime,
            storyline=storyline,
            year=year,
        )
        m.save()
        for d in director_list:
            m.director.add(d)
        for d in actor_list:
            m.actor.add(d)
        for d in writer_list:
            m.writer.add(d)
        m.save()
    else:
        print "-"*80
        print "-"*80
        print "-"*80
        print "-"*80
        print title
        print "-"*80
        print "-"*80
        print "-"*80
        print "-"*80
        m = Movie(
            filename = title.replace(" ","-"),
            title = title,
            titleraw = rawtitle,)
        m.save()


def chopper(words,labMT,labMTvector,outfile,minSize=1000):
  # print "now splitting the text into chunks of size 1000"
  # print "and printing those frequency vectors"
  allFvec = []
  from numpy import floor
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
    print "writing out the file to {0}".format(outfile) 
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

def renameThe(folder):
  query = Movie.objects.all()
  for movie in query:
    filename = movie.filename # .replace(" ","-")
    correctname = filename    
    if filename[0:4] == "The-":
      wrongname = filename[4:]+",-The"
    if filename[0:4] == "A-":
      wrongname = filename[4:]+",-A"
      # try:
      #   shutil.copyfile("/usr/share/nginx/data/moviedata/rawer/"+wrongname+".html.end.beg","/usr/share/nginx/data/moviedata/rawer/"+correctname+".html.end.beg")
      # except:
      #   print wrongname+" rawer .end.beg failed, copy manually"
      # try:
      #   shutil.copyfile("/usr/share/nginx/data/moviedata/raw/"+wrongname+".txt","/usr/share/nginx/data/moviedata/raw/"+correctname+".txt")
      # except:
      #   print wrongname+" raw failed, copy manually"
      # try:
      #   shutil.copyfile("/usr/share/nginx/data/moviedata/rawer/"+wrongname+".html.clean01","/usr/share/nginx/data/moviedata/rawer/"+correctname+".html.clean01")
      # except:
      #   print wrongname+" rawer clean01 failed, copy manually"
    if not correctname == wrongname:
      try:
        shutil.move("/usr/share/nginx/data/moviedata/"+folder+"/"+wrongname+".html","/usr/share/nginx/data/moviedata/"+folder+"/"+correctname+".html")
      except:
        print wrongname+" in "+folder+"  failed, copy manually"

def renameFull(folder):
  f = open('titles-raw.txt','r')
  g = open('titles-clean.txt','r')
  for line in f:
    cleantitle = g.readline().rstrip().replace(" ","-")+".html"
    print cleantitle
    messytitle = line.rstrip().replace(" ","-")+".html"
    print messytitle
    shutil.move("/usr/share/nginx/data/moviedata/"+folder+"/"+messytitle,"/usr/share/nginx/data/moviedata/"+folder+"/"+cleantitle)
  f.close()
  g.close()

def renameFullPass2(folder):
  f = open('titles-raw.txt','r')
  g = open('titles-clean.txt','r')
  for line in f:
    cleantitle = g.readline().rstrip().replace(" ","-")+".html"
    messytitle = line.rstrip().replace(" ","-")+".html"
    try:
      shutil.move("/usr/share/nginx/data/moviedata/"+folder+"/"+messytitle,"/usr/share/nginx/data/moviedata/"+folder+"/"+cleantitle)
      print "renamed "+messytitle
    except:
      pass
  f.close()
  g.close()

def checkClean(folder):
  f = open('titles-raw.txt','r')
  g = open('titles-clean.txt','r')
  if not os.path.isdir("/usr/share/nginx/data/moviedata/"+folder+"/redownload"):
    os.mkdir("/usr/share/nginx/data/moviedata/"+folder+"/redownload")
  for line in f:
    cleantitle = g.readline().rstrip().replace(" ","-")+".html"
    messytitle = line.rstrip().replace(" ","-")+".html"
    # shutil.move("/usr/share/nginx/data/moviedata/"+folder+"/"+messytitle,"/usr/share/nginx/data/moviedata/"+folder+"/"+cleantitle)
    fsize = os.stat("/usr/share/nginx/data/moviedata/"+folder+"/"+cleantitle+".end.beg").st_size
    if fsize < 4000:
      print messytitle
      # shutil.move("/usr/share/nginx/data/moviedata/"+messytitle,"/usr/share/nginx/data/moviedata/"+folder+"/redownload/"+messytitle)
      # use this the first time it is called to attempt to copy it down
      # if not os.path.isfile("/usr/share/nginx/data/moviedata/"+folder+"/redownload/"+messytitle):
      #   try:
      #     subprocess.call("wget http://www.imsdb.com/scripts/"+messytitle.replace("'","\'"),shell=True)
      #   except:
      #     print "wget http://www.imsdb.com/scripts/"+messytitle.replace("'","\'").replace("&","\&")
        
  f.close()
  g.close()

def process():
  # windowSizes = [500,1000,2000,5000,10000]
  windowSizes = [2000]

  u = open("faillog-2015-06-15.txt","a")

  query = Movie.objects.all()
  # query = Movie.objects.filter(title="127 Hours")
  for movie in query:

    filename = movie.filename
    titleraw = movie.titleraw

    print "filename:"
    print filename

    print "titleraw:"
    print titleraw

    if os.path.isfile("/usr/share/nginx/data/moviedata/scriptsClean/"+titleraw.replace(" ","-").replace(".","-")+".txt"):
      print "found file for title:"
      print movie.title
      print "opening scriptsClean/"+titleraw.replace(" ","-").replace(".","-")+".txt"
      f = codecs.open("scriptsClean/"+titleraw.replace(" ","-").replace(".","-")+".txt","r","utf8")
      raw_text_clean = f.read()
      f.close()
      print "opening raw/"+filename+".html.clean04"
      try:
        f = codecs.open("raw/"+filename+".html.clean04","r","utf8")
        raw_text = f.read()
      except UnicodeDecodeError:
        u.write(movie.title)
        u.write("\n")
        u.write("UnicodeDecodeError")
        u.write("\n")
        movie.exclude = True
        movie.excludeReason = "UnicodeDecodeError"
        movie.save()
      except IOError:
        u.write(movie.title)
        u.write("\n")
        u.write("IOError")
        u.write("\n")
        movie.exclude = True
        movie.excludeReason = "IOError"
        movie.save()
      except:
        u.write(movie.title)
        u.write("\n")
        u.write("unknown error")
        u.write("\n")
        movie.exclude = True
        movie.excludeReason = "Unknown"
        movie.save()
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
          movie.exclude = True
          movie.excludeReason = "movie blank"

    else:
      print "movie does not have a file at:"
      print "/usr/share/nginx/data/moviedata/scriptsClean/"+titleraw.replace(" ","-")+".txt"
      movie.exclude = True
      movie.excludeReason = "missing raw file in scriptsClean"
      u.write(movie.title)
      u.write("\n")
      u.write("missing file at ")
      u.write("/usr/share/nginx/data/moviedata/scriptsClean/"+titleraw.replace(" ","-")+".txt")
      u.write("\n")
      
  u.close()

def dictify(words,wordDict):
  for word in words:
    if word in wordDict:
      wordDict[word] += 1
    else:
      wordDict[word] = 1

def process_overallHapps():
  query = Movie.objects.all().filter(exclude=False)
  alltext_dict = dict()
  alltext_labMT_fVec = zeros(10222)
  ignoreWords = ["camera","cuts"]
  for movie in query:

    filename = movie.filename
    titleraw = movie.titleraw
    if filename == "All":
      continue

    print("filename:")
    print(filename)

    f = codecs.open("raw/"+filename+".html.clean04","r","utf8")
    raw_text = f.read()
    f.close()
    lines = raw_text.split("\n")

    # alltext += raw_text + " "
    
    kwords = []
    klines = []
    for i in xrange(len(lines)):
      if lines[i][0:3] != "<b>":
        tmpwords = [x.lower() for x in re.findall(r"[\w\@\#\'\&\]\*\-\/\[\=\;]+",lines[i],flags=re.UNICODE)]
        kwords.extend(tmpwords)
        klines.extend([i for j in xrange(len(tmpwords))])
          
    print("length of the new parse")
    print(len(kwords))
    # not building up a dict anymore, just adding the freq vectors
    # when not saving out the word vectors
    # dictify(kwords,alltext_dict)
    
    rawtext = " ".join(kwords)

    textValence,textFvec = emotion(rawtext,labMT,shift=True,happsList=labMTvector)
    # print(textValence)
    ignoreWords = ["camera","cuts"]
    ignoreWords.extend(movie.ignorewords.split(","))
    # this is just going to block the four nigg* and the specific movie words
    stoppedVec = stopper(textFvec,labMTvector,labMTwordList,stopVal=0.0,ignore=ignoreWords)
    # add this minimally blocked list to the total
    # (since I want to only block these special words for some movies...)
    # a bit convoluted
    alltext_labMT_fVec += stoppedVec

    # # save the completely unstopped list out
    # f = open("word-vectors/full/"+movie.filename+".csv","w")
    # f.write('{0:.0f}'.format(textFvec[0]))
    # for k in xrange(1,len(textFvec)):
    #   f.write(',{0:.0f}'.format(textFvec[k]))
    # f.close()

    # fully stop the vec to compute the happiness
    stoppedVec = stopper(textFvec,labMTvector,labMTwordList,stopVal=2.0,ignore=ignoreWords)
    happs = emotionV(stoppedVec,labMTvector)
    print(happs)
    
    movie.length = len(kwords)
    movie.happs = happs
    movie.save()
    
  # print("now computing for the full thing")
  # # go compute the happs of all the movies mashed together
  # textValence = labMTsenti.scoreTrie(alltext_dict)
  # textFvec = labMTsenti.wordVecifyTrieDict(alltext_dict)
  
  stoppedVec = stopper(alltext_labMT_fVec,labMTvector,labMTwordList,stopVal=2.0,ignore=ignoreWords)
  happs = emotionV(stoppedVec,labMTvector)
  # print(textValence)
  # print(happs)

  # # # create a database entry and save it
  # # m = Movie(filename="All",title="All",titleraw="All",happs=happs,happsStart=0.0,happsEnd=0.0,happsVariance=0.0,happsMin=0.0,happsMax=0.0,happsDiff=0.0,exclude=False)
  m = Movie.objects.filter(filename="All")[0]
  m.happs = happs
  m.save()

  # write out the word vector, not stopped except for the specific words
  f = open("word-vectors/full/"+m.filename+".csv","w")
  f.write('{0:.0f}'.format(alltext_labMT_fVec[0]))
  for k in xrange(1,len(alltext_labMT_fVec)):
    f.write(',{0:.0f}'.format(alltext_labMT_fVec[k]))
  f.close()

def testRE():
  # assume everything is in english
  lang = "english"
  labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+lang+'.txt',returnVector=True)

  windowSizes = [500,1000,2000,5000,10000]

  query = Movie.objects.filter(title=sys.argv[1])
  for movie in query:

    filename = movie.filename # .replace(" ","-")
    # print filename
    if filename[0:4] == "The-":
      # print "starts with the"
      filename = filename[4:]+",-The"
    # print filename

    if os.path.isfile("/usr/share/nginx/data/moviedata/scriptsClean/"+filename+".txt"):
      print movie.title
      f = codecs.open("scriptsClean/"+filename+".txt","r","utf8")
      raw_text = f.read()
      f.close()
    
      words = [x.lower() for x in re.findall(r"[\w\@\#\'\&\]\*\-\/\[\=\;]+",raw_text,flags=re.UNICODE)]

      print len(words)

def fixModels():
  f = open("/usr/share/nginx/data/moviedata/titles-clean.txt","r")
  titles = [line.rstrip() for line in f]
  f.close()
  f = open("/usr/share/nginx/data/moviedata/titles-raw.txt","r")
  rawtitles = [line.rstrip() for line in f]
  f.close()

  missing = []

  for title,rawtitle in zip(titles,rawtitles):
    try:
      m = Movie.objects.get(title=title)
      m.titleraw = rawtitle
      # m.save()
    except:
      # print title
      # print "possible matches"
      # print Movie.objects.filter(title__contains=title.split(" ")[0])
      missing.append(title)
      # scrape(title,rawtitle)
      m = Movie(
        filename = title.replace(" ","-"),
        title = title,
        titleraw = rawtitle,
        happs = 0.0,
        happsStart = 0.0,
        happsEnd = 0.0,
        happsVariance = 0.0,
        happsMin = 0.0,
        happsMax = 0.0,
        happsDiff = 0.0,
        exclude = False)
      # m.save()

  print missing
  print len(Movie.objects.all())
  print len(titles)
  print len(missing)
  
  
if __name__ == "__main__":
  # will rename all of the files in raw, rawer
  folder = 'rawer-take2'
  # renameThe(folder)
  # renameFull(folder)
  # checkClean(folder)
  # folder = 'rawer-take2/redownload'
  # renameFullPass2(folder)
  # checkClean(folder)
  # fixModels()

  # pass the name of the movie via sys arg
  # and this will print out the words
  # testRE()

  # resetExclude()
  # process()
  process_overallHapps()




