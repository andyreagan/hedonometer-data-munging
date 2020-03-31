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
from labMTsimple.storyLab import emotionFileReader, emotionV, shift, stopper
from numpy import float, genfromtxt, zeros

from hedonometer.models import Timeseries

REGIONS = [{'id': '0', 'lang': 'english', 'title': 'VACC', 'type': 'main'}]
DATA_DIR = "/usr/share/nginx/data"
SOURCE_DIR = '/users/j/m/jminot/scratch/labmt/storywrangler_en'

with open("stopwords.csv", "r") as f:
    IGNORE = f.read().split("\n")


def processregion(region, date):
    # check the day file is there
    if not isfile(os.path.join(DATA_DIR, 'word-vectors/{0}/{1}-sum.csv'.format(region["title"].lower(), datetime.datetime.strftime(date, '%Y-%m-%d')))):
        print("proccessing main {0}".format(region["title"]))
        rsync_main(region, date)
        # add_main(date,date+datetime.timedelta(days=1),region)

        if isfile(os.path.join(DATA_DIR, 'word-vectors/{0}/{1}-sum.csv'.format(region["title"].lower(), datetime.datetime.strftime(date, '%Y-%m-%d')))):

            print("found sum file, doing stuff")

            # first time this file moved over here, check the format
            switch_delimiter(',', '\n', os.path.join(DATA_DIR, 'word-vectors/{0}/{1}-sum.csv'.format(
                region["title"].lower(), datetime.datetime.strftime(date, '%Y-%m-%d'))))

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
    for region in REGIONS:
        print("processing region {0} on {1}".format(
            region["title"].lower(), datetime.datetime.strftime(date, '%Y-%m-%d')))
        processregion(region, date)
        print("success")


def loopdates(startdate, enddate):
    while startdate <= enddate:
        allregions(startdate)
        startdate += datetime.timedelta(days=1)


def rsync_main(region, date):
    if not isdir(os.path.join(DATA_DIR, 'word-vectors/{0}'.format(region["title"].lower())):
        mkdir(
            os.path.join(DATA_DIR, 'word-vectors/{0}'.format(region["title"].lower())))

    subprocess.call("rsync -avzr vacc2:{2}/{0}.txt word-vectors/{1}/{0}-sum.csv".format(
        date.strftime('%Y-%m-%d'), region["title"].lower(), SOURCE_DIR), shell=True)


def sumfiles(start, end, wordvec, title, numw):
    curr = copy.copy(start)
    while curr <= end:
        try:
            switch_delimiter(
                ',', '\n', 'word-vectors/{1}/{0}-sum.csv'.format(curr.strftime('%Y-%m-%d'), title))
            a = genfromtxt(
                'word-vectors/{1}/{0}-sum.csv'.format(curr.strftime('%Y-%m-%d'), title), dtype=float)
            wordvec = wordvec + a
        except:
            print('could not load word-vectors/{1}/{0}-sum.csv'.format(
                curr.strftime('%Y-%m-%d'), title))
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

        maincurr = copy.copy(start + datetime.timedelta(days=-1))
        while maincurr < end:
            wordvec = zeros(numw)
            # added the try loop to handle failure inside the sumfiles
            # try:
            [total, date] = sumfiles(maincurr + datetime.timedelta(days=-6), maincurr +
                                     datetime.timedelta(days=0), wordvec, region["title"].lower(), numw)

            # if it's empty, add the word "happy"
            if sum(total) == 0:
                total[3] = 1

            # write the total into a file for date
            f = open('word-vectors/{1}/{0}-prev7.csv'.format(
                date.strftime('%Y-%m-%d'), region["title"].lower()), 'w')
            f.write('\n'.join(['{0:.0f}'.format(x) for x in total]))
            f.close()
            maincurr += datetime.timedelta(days=1)

    if option == 'range':
        labMT, labMTvector, labMTwordList = emotionFileReader(
            stopval=0.0, lang=region["lang"], returnVector=True)
        numw = len(labMTvector)

        wordvec = zeros(numw)

        [total, date] = sumfiles(
            start, end, wordvec, region["title"].lower(), numw)

        # write the total into a file for date
        f = open(outfile, 'w')
        f.write('\n'.join(['{0:.0f}'.format(x) for x in total]))
        f.close()

    if option == 'list':
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
        f = open(outfile, 'w')
        f.write('\n'.join(['{0:.0f}'.format(x) for x in wordvec]))
        f.close()


def timeseries(start, region, useStopWindow=True):
    labMT, labMTvector, labMTwordList = emotionFileReader(
        stopval=0.0, lang=region["lang"], returnVector=True)
    numw = len(labMTvector)

    g = codecs.open('word-vectors/' +
                    region["title"].lower() + '/sumhapps.csv', 'a', 'utf8')
    h = codecs.open('word-vectors/' +
                    region["title"].lower() + '/sumfreq.csv', 'a', 'utf8')

    # loop over time
    currDay = copy.copy(start)

    # empty array
    happsarray = zeros(24)
    dayhappsarray = zeros(1)
    wordarray = [zeros(numw) for i in xrange(24)]
    daywordarray = zeros(numw)

    daywordarray = genfromtxt('word-vectors/' + region["title"].lower(
    ) + '/{0}-sum.csv'.format(currDay.strftime('%Y-%m-%d')), dtype=float)

    # compute happiness of the word vectors
    if useStopWindow:
        stoppedVec = stopper(daywordarray, labMTvector,
                             labMTwordList, ignore=IGNORE)

        happs = emotionV(stoppedVec, labMTvector)
    else:
        happs = emotionV(daywordarray, labMTvector)
    dayhappsarray[0] = happs

    if dayhappsarray[0] > 0:
        # write out the day happs
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

    word_array = genfromtxt('word-vectors/{1}/{0}-sum.csv'.format(
        currDay.strftime('%Y-%m-%d'), region["title"].lower()))
    previous_word_array = genfromtxt(
        'word-vectors/{1}/{0}-prev7.csv'.format(currDay.strftime('%Y-%m-%d'), region["title"].lower()))

    # compute happiness of the word vectors
    word_array_stopped = stopper(
        word_array, labMTvector, labMTwordList, ignore=IGNORE)
    previous_word_array_stopped = stopper(
        previous_word_array, labMTvector, labMTwordList, ignore=IGNORE)
    happs = emotionV(word_array_stopped, labMTvector)
    prevhapps = emotionV(previous_word_array_stopped, labMTvector)

    [sortedMag, sortedWords, sortedType, sumTypes] = shift(
        previous_word_array_stopped, word_array_stopped, labMTvector, labMTwordList)

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

    g = open('shifts/{1}/{0}-metashift.csv'.format(
        currDay.strftime('%Y-%m-%d'), region["title"].lower()), 'w')
    g.write("refH,compH,negdown,negup,posdown,posup")
    g.write("\n{0},{1},{2},{3},{4},{5}".format(prevhapps, happs,
                                               sumTypes[0], sumTypes[1], sumTypes[2], sumTypes[3]))
    g.close()


def sort_sum_happs():
    for region in REGIONS:
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


if __name__ == '__main__':
    # do the rsync
    # start = datetime.datetime(2014,4,15)
    # start = datetime.datetime(2015,2,9)
    # start = datetime.datetime(2015,5,27)
    # end = datetime.datetime(2015,5,27)
    end = datetime.datetime.now()
    end -= datetime.timedelta(hours=end.hour, minutes=end.minute,
                              seconds=end.second, microseconds=end.microsecond)
    start = end - datetime.timedelta(days=40)
    # start = datetime.datetime(2008, 9, 9)
    # start = datetime.datetime(2010, 1, 1)

    loopdates(start, end)
