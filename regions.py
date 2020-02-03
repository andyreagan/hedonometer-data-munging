# regions.py
#
# here's an attempt to sync the geographic timeseries
# using python! stick with python 2 for now
#
# USAGE
#
# python regions.py updateall
# which will update all regions over all possible dates
#
# python regions.py updateweek
# which will get the most recent wekk
#
# in the main file....can easily define a loop over other
# timeframes or specific regions
# (for a specific region, circumvent allregions)
#
# andy reagan
# 2015-02-04

import codecs
import copy
import datetime
import subprocess
import sys
from os import environ, mkdir
from os.path import isdir, isfile

from django.conf import settings
from labMTsimple.storyLab import emotionFileReader, emotionV, stopper, shift
from numpy import float, genfromtxt, zeros

sys.path.append('/home/prod/app')
environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

from hedonometer.models import Timeseries

# regions = [["France","79","french",],["Germany","86","german",],["England","239","english",],["Spain","213","spanish",],["Brazil","32","portuguese",],["Mexico","145","spanish",],["South-Korea","211","korean",],["Egypt","69","arabic",],["Australia","14","english",],["New-Zealand","160","english",],["Canada","41","english",],["Canada-fr","41","french",],]

regions = [{'id': '79', 'lang': 'french', 'title': 'France', 'type': 'region'},
           {'id': '86', 'lang': 'german', 'title': 'Germany', 'type': 'region'},
           {'id': '239', 'lang': 'english', 'title': 'England', 'type': 'region'},
           {'id': '213', 'lang': 'spanish', 'title': 'Spain', 'type': 'region'},
           {'id': '32', 'lang': 'portuguese', 'title': 'Brazil', 'type': 'region'},
           {'id': '145', 'lang': 'spanish', 'title': 'Mexico', 'type': 'region'},
           {'id': '211', 'lang': 'korean', 'title': 'South-Korea', 'type': 'region'},
           {'id': '69', 'lang': 'arabic', 'title': 'Egypt', 'type': 'region'},
           {'id': '14', 'lang': 'english', 'title': 'Australia', 'type': 'region'},
           {'id': '160', 'lang': 'english', 'title': 'New-Zealand', 'type': 'region'},
           {'id': '41', 'lang': 'english', 'title': 'Canada', 'type': 'region'},
           {'id': '41', 'lang': 'french', 'title': 'Canada-fr', 'type': 'region'},
           {'id': '0', 'lang': 'english', 'title': 'VACC', 'type': 'main'}]

regions = [{'id': '0', 'lang': 'english', 'title': 'VACC', 'type': 'main'}]

with open("stopwords.csv", "r") as f:
    IGNORE = f.read().split("\n")


def processregion(region, date):
    # check the day file is there
    if not isfile('/usr/share/nginx/data/word-vectors/{0}/{1}-sum.csv'.format(region["title"].lower(), datetime.datetime.strftime(date, '%Y-%m-%d'))):
        # if True:
        if region["type"] == "region":
            print("proccessing {0}".format(region["title"]))
            rsync(region, date)
        elif region["type"] == "main":
            print("proccessing main {0}".format(region["title"]))
            rsync_main(region, date)
            # add_main(date,date+datetime.timedelta(days=1),region)
        else:
            print("unknown region type {0}".format(region["type"]))

        if isfile('/usr/share/nginx/data/word-vectors/{0}/{1}-sum.csv'.format(region["title"].lower(), datetime.datetime.strftime(date, '%Y-%m-%d'))):

            print("found sum file, doing stuff")

            # first time this file moved over here, check the format
            switch_delimiter(',', '\n', '/usr/share/nginx/data/word-vectors/{0}/{1}-sum.csv'.format(
                region["title"].lower(), datetime.datetime.strftime(date, '%Y-%m-%d')))

            # add up the previous vectors
            rest('prevvectors', date, date, region)

            timeseries(date, region, useStopWindow=True)

            preshift(date, region)

            if not region["type"] == "main":
                updateModel(date, region)

            sort_sum_happs()
        else:
            pass


def allregions(date):
    for region in regions:
        print "processing region {0} on {1}".format(
            region["title"].lower(), datetime.datetime.strftime(date, '%Y-%m-%d'))
        # try:
        processregion(region, date)
        print "success"
        # except:
        #     print "failed"


def loopdates(startdate, enddate):
    while startdate <= enddate:
        allregions(startdate)
        startdate += datetime.timedelta(days=1)


def rsync_main(region, date):
    if not isdir('/usr/share/nginx/data/word-vectors/{0}'.format(region["title"].lower())):
        mkdir(
            '/usr/share/nginx/data/word-vectors/{0}'.format(region["title"].lower()))
    DIR = '/users/j/m/jminot/scratch/labmt/storywrangler_en'
    subprocess.call("rsync -avzr vacc2:{2}/{0}.txt word-vectors/{1}/{0}-sum.csv".format(
        date.strftime('%Y-%m-%d'), region["title"].lower(), DIR), shell=True)


def rsync(region, date):
    # print "trying to get the file"
    if isdir('/usr/share/nginx/data/word-vectors/{0}'.format(region["title"].lower())):
        # try to get the file
        subprocess.call("rsync -avzr --ignore-existing vacc1:/users/a/r/areagan/fun/twitter/jake/pullTweets/word-vectors/{1}-{0}-word-vector.csv /usr/share/nginx/data/word-vectors/{2}/{1}-sum.csv".format(
            region["title"], datetime.datetime.strftime(date, '%Y-%m-%d'), region["title"].lower()), shell=True)
    else:
        mkdir(
            '/usr/share/nginx/data/word-vectors/{0}'.format(region["title"].lower()))
        subprocess.call("rsync -avzr --ignore-existing vacc1:/users/a/r/areagan/fun/twitter/jake/pullTweets/word-vectors/{1}-{0}-word-vector.csv /usr/share/nginx/data/word-vectors/{2}/{1}-sum.csv".format(
            region["title"], datetime.datetime.strftime(date, '%Y-%m-%d'), region["title"].lower()), shell=True).communicate()


def sumfiles(start, end, wordvec, title, numw):
    curr = copy.copy(start)
    while curr <= end:
        # print "adding {0}".format(curr.strftime('%Y-%m-%d'))
        try:
            switch_delimiter(
                ',', '\n', 'word-vectors/{1}/{0}-sum.csv'.format(curr.strftime('%Y-%m-%d'), title))
            a = genfromtxt(
                'word-vectors/{1}/{0}-sum.csv'.format(curr.strftime('%Y-%m-%d'), title), dtype=float)
            wordvec = wordvec+a
        except:
            # print "could not load {0}".format(curr.strftime('%Y-%m-%d'))
            print 'could not load word-vectors/{1}/{0}-sum.csv'.format(
                curr.strftime('%Y-%m-%d'), title)
            # raise
            # pass
        curr += datetime.timedelta(days=1)

    return wordvec, curr


def add_main(start, end, region):
    fifteen_minutes = datetime.timedelta(minutes=15)
    labMT, labMTvector, labMTwordList = emotionFileReader(
        stopval=0.0, lang=region["lang"], returnVector=True)
    numw = len(labMTvector)
    my_array = zeros(numw)

    # check that all of the files are there
    date = start
    allfiles = True
    n_files = 0
    while date < end:
        if not isfile(date.strftime('word-vectors/{0}/%Y-%m-%d/%Y-%m-%d-%H-%M.csv'.format(region["title"].lower()))):
            print('missing {0}'.format(date.strftime(
                'word-vectors/{0}/%Y-%m-%d/%Y-%m-%d-%H-%M.csv'.format(region["title"].lower()))))
            allfiles = False
            # break
        else:
            n_files += 1
        date += fifteen_minutes
    # can either need all of the files, or not
    # using the if True works for doing the full historical one
    # if allfiles or n_files > (24*4-2):
    if allfiles:
        print('all files found')
    # if True:
        date = start
        while date < end:
            if isfile(date.strftime('word-vectors/{0}/%Y-%m-%d/%Y-%m-%d-%H-%M.csv'.format(region["title"].lower()))):
                switch_delimiter(',', '\n', date.strftime(
                    'word-vectors/{0}/%Y-%m-%d/%Y-%m-%d-%H-%M.csv'.format(region["title"].lower())))
                a = genfromtxt(date.strftime(
                    'word-vectors/{0}/%Y-%m-%d/%Y-%m-%d-%H-%M.csv'.format(region["title"].lower())), dtype=float)
                print(date.strftime(
                    'word-vectors/{0}/%Y-%m-%d/%Y-%m-%d-%H-%M.csv'.format(region["title"].lower())))
                print(a)
                my_array += a
            date += fifteen_minutes
        print(my_array)
        if sum(my_array) > 0:
            f = open(start.strftime(
                'word-vectors/{0}/%Y-%m-%d-sum.csv'.format(region["title"].lower())), 'w')
            f.write('\n'.join(['{0:.0f}'.format(x) for x in my_array]))
            f.close()
    else:
        print('not all files found')


def rest(option, start, end, region, outfile='test.csv', days=[]):
    # if the option is range, pass it an outfile to write to
    # if the option is list, pass it an outfile and days list
    if option == 'prevvectors':
        labMT, labMTvector, labMTwordList = emotionFileReader(
            stopval=0.0, lang=region["lang"], returnVector=True)
        numw = len(labMTvector)

        maincurr = copy.copy(start+datetime.timedelta(days=-1))
        while maincurr < end:
            wordvec = zeros(numw)
            # added the try loop to handle failure inside the sumfiles
            # try:
            [total, date] = sumfiles(maincurr+datetime.timedelta(days=-6), maincurr +
                                     datetime.timedelta(days=0), wordvec, region["title"].lower(), numw)

            # if it's empty, add the word "happy"
            if sum(total) == 0:
                total[3] = 1

            # write the total into a file for date
            # print "printing to {0}-prev7.csv".format(date.strftime('%Y-%m-%d'))
            f = open('word-vectors/{1}/{0}-prev7.csv'.format(
                date.strftime('%Y-%m-%d'), region["title"].lower()), 'w')
            f.write('\n'.join(['{0:.0f}'.format(x) for x in total]))
            f.close()
            # except:
            #     print "failed on {0}".format(date.strftime('%Y-%m-%d'))
            #     print "-------------------------------"
            maincurr += datetime.timedelta(days=1)

    if option == 'range':
        labMT, labMTvector, labMTwordList = emotionFileReader(
            stopval=0.0, lang=region["lang"], returnVector=True)
        numw = len(labMTvector)

        wordvec = zeros(numw)

        [total, date] = sumfiles(
            start, end, wordvec, region["title"].lower(), numw)

        # write the total into a file for date
        # print "printing to {0}".format(date.strftime('%Y-%m-%d'))
        f = open(outfile, 'w')
        f.write('\n'.join(['{0:.0f}'.format(x) for x in total]))
        f.close()
        # except:
        #     print "failed on {0}".format(date.strftime('%Y-%m-%d'))
        #     print "-------------------------------"

    if option == 'list':
        # print "heads up, the second word after list needs to be the language"
        labMT, labMTvector, labMTwordList = emotionFileReader(
            stopval=0.0, lang=region["lang"], returnVector=True)
        numw = len(labMTvector)

        wordvec = zeros(numw)
        for day in days:
            # this should handle the array object by reference
            [tmp, date] = sumfiles(
                day, day, wordvec, region["title"].lower(), numw)
            wordvec += tmp

        # write the total into a file for date
        # print "printing to {0}".format(outfile)
        f = open(outfile, 'w')
        f.write('\n'.join(['{0:.0f}'.format(x) for x in wordvec]))
        f.close()


def timeseries(start, region, useStopWindow=True):
    labMT, labMTvector, labMTwordList = emotionFileReader(
        stopval=0.0, lang=region["lang"], returnVector=True)
    numw = len(labMTvector)

    # print "opening in append mode"
    g = codecs.open('word-vectors/' +
                    region["title"].lower()+'/sumhapps.csv', 'a', 'utf8')
    h = codecs.open('word-vectors/' +
                    region["title"].lower()+'/sumfreq.csv', 'a', 'utf8')

    # loop over time
    currDay = copy.copy(start)

    # empty array
    happsarray = zeros(24)
    dayhappsarray = zeros(1)
    wordarray = [zeros(numw) for i in xrange(24)]
    daywordarray = zeros(numw)

    # print 'reading word-vectors/'+region["title"].lower()+'/{0}'.format(currDay.strftime('%Y-%m-%d-sum.csv'))

    daywordarray = genfromtxt('word-vectors/'+region["title"].lower(
    )+'/{0}-sum.csv'.format(currDay.strftime('%Y-%m-%d')), dtype=float)

    # # try
    # f = codecs.open('word-vectors/'+region["title"].lower()+'/{0}-sum.csv'.format(currDay.strftime('%Y-%m-%d')),'r','utf8')
    # daywordarray = array(map(float,f.read().split(',')[0:numw]))
    # f.close()
    # # print daywordarray
    # # print len(daywordarray)
    # compute happiness of the word vectors
    if useStopWindow:
        stoppedVec = stopper(daywordarray, labMTvector, labMTwordList, ignore=IGNORE)
                             
        happs = emotionV(stoppedVec, labMTvector)
    else:
        happs = emotionV(daywordarray, labMTvector)
    dayhappsarray[0] = happs

    if dayhappsarray[0] > 0:
        # write out the day happs
        # print 'writing word-vectors/{1}/{0}-happs'.format(currDay.strftime('%Y-%m-%d'),region["title"].lower())
        f = codecs.open('word-vectors/{1}/{0}-happs.csv'.format(
            currDay.strftime('%Y-%m-%d'), region["title"].lower()), 'w', 'utf8')
        f.write('{0}'.format(dayhappsarray[0]))
        f.close()

        # add to main file
        g.write('{0},{1}\n'.format(
            currDay.strftime('%Y-%m-%d'), dayhappsarray[0]))

    # always write out the frequency
    h.write('{0},{1:.0f}\n'.format(
        currDay.strftime('%Y-%m-%d'), sum(daywordarray)))

    g.close()
    h.close()


def updateModel(start, region):
    # go get the database model
    t = Timeseries.objects.get(title=region["title"])
    t.endDate = start
    t.save()


def preshift(start, region):
    labMT, labMTvector, labMTwordList = emotionFileReader(
        stopval=0.0, lang=region["lang"], returnVector=True)
    numw = len(labMTvector)

    # loop over time
    currDay = copy.copy(start)

    # # empty array
    # wordarray = zeros(numw)
    # prevwordarray = zeros(numw)

    # # print 'reading word-vectors/{1}/{0}'.format(currDay.strftime('%Y-%m-%d-sum.csv'),region["title"].lower())
    # f = codecs.open('word-vectors/{1}/{0}-sum.csv'.format(currDay.strftime('%Y-%m-%d'),region["title"].lower()),'r','utf8')
    # wordarray = array(map(float,f.read().split(',')[0:numw]))
    # f.close()

    # # print 'reading word-vectors/{1}/{0}'.format(currDay.strftime('%Y-%m-%d-prev7.csv'),region["title"].lower())
    # f = codecs.open('word-vectors/{1}/{0}-prev7.csv'.format(currDay.strftime('%Y-%m-%d'),region["title"].lower()),'r','utf8')
    # prevwordarray = array(map(float,f.read().split(',')[0:numw]))
    # f.close()
    # # print daywordarray
    # # print len(wordarray)
    # # print len(prevwordarray)

    word_array = genfromtxt('word-vectors/{1}/{0}-sum.csv'.format(
        currDay.strftime('%Y-%m-%d'), region["title"].lower()))
    previous_word_array = genfromtxt(
        'word-vectors/{1}/{0}-prev7.csv'.format(currDay.strftime('%Y-%m-%d'), region["title"].lower()))

    # compute happiness of the word vectors
    word_array_stopped = stopper(word_array, labMTvector, labMTwordList, ignore=IGNORE)
    previous_word_array_stopped = stopper(previous_word_array, labMTvector, labMTwordList, ignore=IGNORE)
    happs = emotionV(word_array_stopped, labMTvector)
    prevhapps = emotionV(previous_word_array_stopped, labMTvector)
    # print happs

    [sortedMag, sortedWords, sortedType, sumTypes] = shift(
        previous_word_array_stopped, word_array_stopped, labMTvector, labMTwordList)
    # print sortedMag[:10]
    # print sortedWords[:10]
    # print sortedType[:10]
    # print sumTypes

    # print 'writing shifts/{1}/{0}-shift.csv'.format(currDay.strftime('%Y-%m-%d'),region["title"].lower())
    g = codecs.open('shifts/{1}/{0}-shift.csv'.format(
        currDay.strftime('%Y-%m-%d'), region["title"].lower()), 'w', 'utf8')
    g.write("mag,word,type")
    for i in xrange(10):
        g.write("\n")
        g.write(str(sortedMag[i]))
        g.write(",")
        g.write(sortedWords[i])
        g.write(",")
        g.write(str(sortedType[i]))
    g.close()

    # print 'writing shifts/{1}/{0}-metashift.csv'.format(currDay.strftime('%Y-%m-%d'),region["title"].lower())
    g = open('shifts/{1}/{0}-metashift.csv'.format(
        currDay.strftime('%Y-%m-%d'), region["title"].lower()), 'w')
    g.write("refH,compH,negdown,negup,posdown,posup")
    g.write("\n{0},{1},{2},{3},{4},{5}".format(prevhapps, happs,
                                               sumTypes[0], sumTypes[1], sumTypes[2], sumTypes[3]))
    g.close()


def makeshiftdirectories():
    for region in regions:
        mkdir(
            '/usr/share/nginx/data/shifts/{0}'.format(region["title"].lower()))


def emptysumhapps():
    for region in regions:
        f = open(
            '/usr/share/nginx/data/word-vectors/{0}/sumhapps.csv'.format(region["title"].lower()), 'w')
        f.write('date,value\n')
        f.close()
        f = open(
            '/usr/share/nginx/data/word-vectors/{0}/sumfreq.csv'.format(region["title"].lower()), 'w')
        f.write('date,value\n')
        f.close()


def sort_sum_happs():
    for region in regions:
        f = open(
            '/usr/share/nginx/data/word-vectors/{0}/sumhapps.csv'.format(region["title"].lower()), 'r')
        # skip the header
        f.readline()
        dates = []
        happss = []
        for line in f:
            d, h = line.rstrip().split(',')
            date = datetime.datetime.strptime(d, '%Y-%m-%d')
            happs = float(h)
            # make sure no duplicates
            if not date in dates:
                dates.append(date)
                happss.append(happs)
            # later dates take precendence
            else:
                happss[dates.index(date)] = happs
        f.close()
        # now sort
        indexer = sorted(list(range(len(dates))), key=lambda k: dates[k])
        dates_sorted = [dates[i] for i in indexer]
        happss_sorted = [happss[i] for i in indexer]
        f = open(
            '/usr/share/nginx/data/word-vectors/{0}/sumhapps.csv'.format(region["title"].lower()), 'w')
        f.write('date,value\n')
        for d, h in zip(dates_sorted, happss_sorted):
            f.write('{0},{1}\n'.format(d.strftime('%Y-%m-%d'), h))
        f.close()

        f = open(
            '/usr/share/nginx/data/word-vectors/{0}/sumfreq.csv'.format(region["title"].lower()), 'r')
        # skip the header
        f.readline()
        dates = []
        freqs = []
        for line in f:
            tmp = line.rstrip().split(',')
            if len(tmp) == 2:
                d, fr = tmp
                date = datetime.datetime.strptime(d, '%Y-%m-%d')
                freq = float(fr)
                # make sure no duplicates
                if not date in dates:
                    dates.append(date)
                    freqs.append(freq)
        f.close()
        # now sort
        indexer = sorted(list(range(len(dates))), key=lambda k: dates[k])
        dates_sorted = [dates[i] for i in indexer]
        freqs_sorted = [freqs[i] for i in indexer]
        f = open(
            '/usr/share/nginx/data/word-vectors/{0}/sumfreq.csv'.format(region["title"].lower()), 'w')
        f.write('date,value\n')
        for d, fr in zip(dates_sorted, freqs_sorted):
            f.write('{0},{1:.0f}\n'.format(d.strftime('%Y-%m-%d'), fr))
        f.close()


def switch_delimiter(from_delim, to_delim, filename):
    # switch_delimiter(from_delim,to_delim,filename)
    #
    # attempt to swith the delimiter of a file, safely
    # tested briefly on the `realtime-parse` data
    f = open(filename, 'r')
    raw = f.read()
    f.close()
    if from_delim in raw:
        my_array = list(map(float, raw.rstrip(from_delim).split(from_delim)))
        f = open(filename, 'w')
        f.write(to_delim.join(['{0:.0f}'.format(x) for x in my_array]))
        f.close()


def printlinks():
    for region in regions:
        print 'http://hedonometer.org/{0}/'.format(region["title"].lower())


if __name__ == '__main__':

    # makeshiftdirectories()

    # emptysumhapps()

    # printlinks()

    # do the rsync
    # start = datetime.datetime(2014,4,15)
    # start = datetime.datetime(2015,2,9)
    # start = datetime.datetime(2015,5,27)
    # end = datetime.datetime(2015,5,27)
    end = datetime.datetime.now()
    end -= datetime.timedelta(hours=end.hour, minutes=end.minute,
                              seconds=end.second, microseconds=end.microsecond)
    start = end - datetime.timedelta(days=40)
    start = datetime.datetime(2008, 9, 9)
    # start = datetime.datetime(2010,1,1)

    loopdates(start, end)
