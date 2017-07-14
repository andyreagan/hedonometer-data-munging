# chop.py
#
# chop up a text into a bunch of frequency vectors of length
# 
# USAGE
#
# python chop.py data/count-of-monte-cristo.txt output french

from tqdm import trange
import codecs # handle utf8
import re
from numpy import floor,zeros,array
import shutil
import subprocess
import unirest
import datetime

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
      # note that this moved to another python file:
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
  # process_overallHapps()

  # # check that the files all exist
  # movies = Movie.objects.all()
  # for m in movies:
  #   if not os.path.isfile("scriptsClean/"+m.titleraw.replace(" ","-").replace(".","-")+".txt"):
  #     print(m.title)
  #     print("missing scriptsClean file")
  #     # print "opening scriptsClean/"+titleraw.replace(" ","-").replace(".","-")+".txt"
  #     # f = codecs.open("scriptsClean/"+titleraw.replace(" ","-").replace(".","-")+".txt","r","utf8")
  #     # raw_text_clean = f.read()
  #     # f.close()
  #   if not os.path.isfile("raw/"+m.filename+".html"):
  #     print(m.title)
  #     print("found raw file")
  #     # print "opening raw/"+filename+".html.clean04"
  #     # try:
  #     #   f = codecs.open("raw/"+filename+".html.clean04","r","utf8")      

  # # check that the files all nonzero
  # movies = Movie.objects.all()
  # for m in movies:
  #   a = os.stat("scriptsClean/"+m.titleraw.replace(" ","-").replace(".","-")+".txt")
  #   if a.st_size < 100:
  #     print("empty file: "+"scriptsClean/"+m.titleraw.replace(" ","-").replace(".","-")+".txt")
  #   a = os.stat("raw/"+m.filename+".html")
  #   if a.st_size < 1000:
  #     print("empty file: "+"raw/"+m.filename+".html")

  # # movies = Movie.objects.filter(title="They")
  # movies = Movie.objects.all()
  # # for m in movies:
  # for i in trange(len(movies)):
  #   m = movies[i]
  #   # if not os.path.isfile("raw/"+m.filename+".html"):
  #   # print(m.title)
  #   # print("opening raw/"+filename+".html")
  #   # try:
  #   #     f = codecs.open("raw/"+m.filename+".html","r","utf8")
  #   #     raw = f.read()
  #   #     f.close()
  #   # except UnicodeDecodeError:
  #   #     f = codecs.open("raw/"+m.filename+".html","r","iso8859")
  #   #     raw = f.read()
  #   #     f.close()
  #   #     f = codecs.open("raw/"+m.filename+".html","w","utf8")
  #   #     f.write(raw)
  #   #     f.close()
  #   # except:
  #   #   print(m.title)
  #   #   print("couldn't read raw/"+m.filename+".html")
  #   #   print("Unexpected error:", sys.exc_info()[0])
  #   f = codecs.open("raw/"+m.filename+".html","r","utf8")
  #   raw = f.read()
  #   lines = raw.split("\n")
  #   f.close()
  #   # if "<pre>" not in raw:
  #   if len(re.findall(r"<pre.*?>",raw,flags=re.IGNORECASE))==0:
  #     print(m.title)
  #     if len(re.findall(r"<body.*?>",raw,flags=re.IGNORECASE))==0:
  #     # if "<body>" not in raw:
  #       print("no body either")
  #     # else:
  #     #     for i,line in enumerate(raw.split("\n")):
  #     #         if len(re.findall(r"<body.*?>",line,flags=re.IGNORECASE))>0:
  #     #             print(raw.split("\n")[i:i+10])        
  #     if len(re.findall(r"scrtext",raw,flags=re.IGNORECASE))==0:
  #       # if "<body>" not in raw:
  #       print("didn't find scrtext")
  #     else:
  #       found_end = False
  #       found_beg = False
  #       for i,line in enumerate(lines):
  #         if len(re.findall(r"scrtext",line,flags=re.IGNORECASE))>0:
  #           # print(raw.split("\n")[i:i+10])
  #           found_beg = True
  #           scrline = i
  #           print(line)
  #           if "<body>" not in line:
  #             print(lines[i:i+5])
  #           lines[i] = line.replace("<body>","<body><pre>")
  #           print(lines[i])
  #         if len(re.findall(r"</table>",line,flags=re.IGNORECASE))>0 and found_beg and not found_end:
  #           found_end = True
  #           lines[i] = line.replace("</table>","</pre></table>")
  #           print(lines[i])
  #       f = codecs.open("raw/"+m.filename+".html","w","utf8")
  #       f.write("\n".join(lines))
  #       f.close()
  #   # elif len(re.findall(r"<pre.*?>(.*?)</pre>",raw,flags=re.IGNORECASE|re.DOTALL))!=1:
  #   #   # print(len(re.findall(r"(?:<pre.*?>.*?)?<pre.*?>(.*?)</pre>",raw,flags=re.IGNORECASE|re.DOTALL)))
  #   #   print(len(re.findall(r"<pre.*?>(.*?)</pre>",raw,flags=re.IGNORECASE|re.DOTALL)))
  #   #   print(m.title)
  #   # script = "\n".join(re.findall(r"<pre.*?>(.*?)</pre>",raw,flags=re.IGNORECASE|re.DOTALL))
  #   # f = codecs.open("raw/"+m.filename+".txt","w","utf8")
  #   # f.write(script)
  #   # f.close()
  #   beg_line = len(lines)
  #   end_line = 0
  #   for i,line in enumerate(lines):
  #     if len(re.findall(r"<pre.*?>",line,flags=re.IGNORECASE|re.DOTALL))>0:
  #       beg_line = min(i,beg_line)
  #     if len(re.findall(r"</pre.*?>",line,flags=re.IGNORECASE|re.DOTALL))>0:
  #       end_line = i
  #   script = "\n".join(lines[beg_line:end_line])
  #   f = codecs.open("raw/"+m.filename+".txt","w","utf8")
  #   f.write(script)
  #   f.close()


#     # these files have good annotations
# #     raw/Ace-Ventura-Pet-Detective.html
# # raw/At-First-Sight.html
# # raw/Cube.html
# # raw/Days-of-Heaven.html
# # raw/Erik-the-Viking.html
# # raw/Four-Feathers.html
# # raw/Get-Shorty.html
# # raw/Highlander-Endgame.html
# # raw/John-Q.html
# # raw/Never-Been-Kissed.html
# # raw/Real-Genius.html
# # raw/Red-Planet.html
# # raw/The-Saint.html
# # raw/True-Romance.html

# # get rid of insides of comments, scripts, stylesheets
# # remove html markup, keeping: "title", "p", "b"

    # # print(re.findall("<!-->",script))
    # script = re.sub("<!--.*?-->","",script,flags=re.DOTALL|re.IGNORECASE)
    # script = re.sub("<script.*?</script>","",script,flags=re.DOTALL|re.IGNORECASE)
    # script = re.sub("<style.*?</style>","",script,flags=re.DOTALL|re.IGNORECASE)
    # script = re.sub("<style.*?</style>","",script,flags=re.DOTALL|re.IGNORECASE)
    # script = re.sub("<(?!b>|/b>|title>|/title>|p .*?>|p>|/p>).*?>","",script,flags=re.DOTALL|re.IGNORECASE)
    # script = re.sub("\n</b>","</b>\n",script,flags=re.IGNORECASE)
    # script = re.sub("<b>[ ]*</b>","",script,flags=re.IGNORECASE)
    # f = codecs.open("raw/"+m.filename+".txt.clean01","w","utf8")
    # f.write(script)
    # f.close()
    # # if "ID=\"dia\"" in script:
    # #     print(m.title)
    # #     print(set(re.findall("<p id=\"(.*?)\">",script,re.IGNORECASE)))
    # # set([u'right', u'spkdir', u'dia', u'speaker', u'act', u'slug'])
    # # grep -i slug raw/True-Romance.txt.clean01

  # # read the clean01 files...
  # movies = Movie.objects.all()
  # # for m in movies:
  # lengths = []
  # for i in trange(len(movies)):
  #   m = movies[i]
  #   f = codecs.open("raw/"+m.filename+".txt.clean01","r","utf8")
  #   script = f.read()
  #   f.close()
  #   lengths.append(len(script.split("\n")))
  #   if len(script.split("\n")) < 100:
  #     print("raw/"+m.filename+".txt.clean02")
  #     f = codecs.open("raw/"+m.filename+".txt.clean01","w","utf8")
  #     f.write(re.sub("  ([ ]*)","\n  \\1",script))
  #     f.close()      
  # print(sorted(lengths)[:40])
  # ind = sorted(range(len(movies)),key=lambda i:lengths[i])
  # sorted_movies = [(movies[i],lengths[i]) for i in ind]
  # print(sorted_movies[:40])

  # some are all on one line:
  # American Outlaws, Made, Training Day
  # "fixed" with the above
     
  # movies = Movie.objects.all()
  filenames = open("movie-title-list.txt","r").read().split("\n")
  for i in trange(len(filenames)):
    # m = movies[i]
    # print(m.title)
    f = codecs.open("raw/"+filenames[i]+".txt.clean01","r","utf8")
    script = f.read()
    f.close()
    lines = script.split("\n")
    types = ["u" for line in lines]
    line_types = {"u":"unknown",
     "b":"blank",
     "s":"speaker",
     "a":"action",
     "p":"speaking direction",
     "d":"dialogue",
     "l":"slug (scene)",
     "r":"right (cut to, etc)",}

    bold_spacings = []
    general_spacings = []
    for i,line in enumerate(lines):
      blank = re.findall(r"^[ ]*$",line)
      if len(blank)>0:
        types[i] = "b"
        continue
      bold = re.findall(r"<b>([ ]*)([A-Z\. \-'\(\)/:0-9\#]+)</b>",line)
      if len(bold) > 0:
        # print(bold)
        space = bold[0][0]
        bold_spacings.append(len(space))
        text = bold[0][1].rstrip(" ")
        types[i] = "l"
        # lines[i] = space+text
        continue
      line_match = re.findall(r"^([ ]*)(.*?)$",line)
      if len(line_match) > 0:
        # if i<100:
        #   print(line_match)
        space = line_match[0][0]
        general_spacings.append(len(space))
        text = line_match[0][1].rstrip(" ")
        types[i] = "a"
        # lines[i] = space+text
        
    # print(bold_spacings[:100])
    # print(np.mean(bold_spacings))
    # print(general_spacings[:100])
    # print(np.mean(general_spacings))
    for i,line in enumerate(lines):
      blank = re.findall(r"^[ ]*$",line)
      if len(blank)>0:
        types[i] = "b"
        continue
      bold = re.findall(r"<b>([ ]*)([A-Z\. \-'\(\)/:0-9\#]+)</b>",line)
      if len(bold) > 0:
        space = bold[0][0]
        # this makes it a speaker
        if len(space) > np.mean(bold_spacings):
          types[i] = "s"
        text = bold[0][1].rstrip(" ")
        lines[i] = space+text
        continue
      line_match = re.findall(r"^([ ]*)(.*?)$",line)
      if len(line_match) > 0:
        space = line_match[0][0]
        if len(space) > np.mean(general_spacings):
          types[i] = "d"
    f = codecs.open("raw/"+filenames[i]+".script","w","utf8")
    f.write("\n".join([types[i].upper()+lines[i] for i in range(len(lines))]))
    f.close()
