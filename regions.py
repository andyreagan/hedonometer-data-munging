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
import os
from os import mkdir
from os.path import isdir, isfile

import click
from labMTsimple.storyLab import emotionFileReader, emotionV, shift, stopper
from numpy import float, genfromtxt, zeros

from hedonometer.models import Timeseries

DATA_DIR = "/usr/share/nginx/data"
with open(os.path.join(DATA_DIR, Timeseries.objects.all()[0].directory, "stopwords.csv"), "r") as f:
    IGNORE = f.read().split("\n")


def processregion(region, date):
    # check the day file is there
    sumfile = os.path.join(DATA_DIR, region.directory, region.wordVecDir, datetime.datetime.strftime(date, '%Y-%m-%d-sum.csv'))
    if not isfile(sumfile):
        print("proccessing {0} for {1}".format(region.title, sumfile))
        rsync_main(region, date)

        if isfile(sumfile):
            print("found sum file, doing stuff")

            # first time this file moved over here, check the format
            switch_delimiter(',', '\n', sumfile)

            # add up the previous vectors
            rest('prevvectors', date, date, region)

            timeseries(date, region, useStopWindow=True)

            preshift(date, region)

            # updateModel(date, region)

            sort_sum_happs(region)


def allregions(date):
    for region in Timeseries.objects.all():
        print("processing region {0} on {1}".format(
            region.title,
            datetime.datetime.strftime(date, '%Y-%m-%d'))
        )
        processregion(region, date)
        print("success")


def loopdates(startdate, enddate):
    while startdate <= enddate:
        allregions(startdate)
        startdate += datetime.timedelta(days=1)


def rsync_main(region, date):
    wordvec_dir = os.path.join(DATA_DIR, region.directory, region.wordVecDir)
    print(wordvec_dir)
    if not isdir(wordvec_dir):
        print("creating", wordvec_dir)
        mkdir(wordvec_dir)
    command = "rsync -avzr vacc2:{source_file} {dest_file}".format(
        source_file=os.path.join(region.sourceDir, date.strftime('%Y-%m-%d.txt')),
        dest_file=os.path.join(wordvec_dir, date.strftime('%Y-%m-%d-sum.csv'))
    )
    print(command)
    subprocess.call(command,shell=True)


def sumfiles(start, end, wordvec, title, numw):
    curr = copy.copy(start)
    while curr <= end:
        sumfile = os.path.join(
            DATA_DIR,
            title,
            curr.strftime('%Y-%m-%d-sum.csv')
        )
        try:
            switch_delimiter(',', '\n', sumfile)
            a = genfromtxt(sumfile, dtype=float)
            wordvec = wordvec + a
        except:
            print('could not load {0}'.format(sumfile))
        curr += datetime.timedelta(days=1)

    return wordvec, curr


def rest(option, start, end, region, outfile='test.csv', days=[]):
    # if the option is range, pass it an outfile to write to
    # if the option is list, pass it an outfile and days list
    if option == 'prevvectors':
        labMT, labMTvector, labMTwordList = emotionFileReader(
            stopval=0.0, lang=region.language, returnVector=True)
        numw = len(labMTvector)

        maincurr = copy.copy(start + datetime.timedelta(days=-1))
        while maincurr < end:
            wordvec = zeros(numw)
            # added the try loop to handle failure inside the sumfiles
            # try:
            [total, date] = sumfiles(maincurr + datetime.timedelta(days=-6), maincurr +
                                     datetime.timedelta(days=0), wordvec, os.path.join(region.directory, region.wordVecDir), numw)

            # if it's empty, add the word "happy"
            if sum(total) == 0:
                total[3] = 1
            sumfile = os.path.join(
                DATA_DIR,
                region.directory,
                region.wordVecDir,
                date.strftime('%Y-%m-%d-prev7.csv')
            )
            # write the total into a file for date
            f = open(sumfile, 'w')
            f.write('\n'.join(['{0:.0f}'.format(x) for x in total]))
            f.close()
            maincurr += datetime.timedelta(days=1)

    if option == 'range':
        labMT, labMTvector, labMTwordList = emotionFileReader(
            stopval=0.0, lang=region.language, returnVector=True)
        numw = len(labMTvector)

        wordvec = zeros(numw)

        [total, date] = sumfiles(
            start, end, wordvec, os.path.join(region.directory, region.wordVecDir), numw)

        # write the total into a file for date
        f = open(outfile, 'w')
        f.write('\n'.join(['{0:.0f}'.format(x) for x in total]))
        f.close()

    if option == 'list':
        labMT, labMTvector, labMTwordList = emotionFileReader(
            stopval=0.0, lang=region.language, returnVector=True)
        numw = len(labMTvector)

        wordvec = zeros(numw)
        for day in days:
            # this should handle the array object by reference
            [tmp, date] = sumfiles(
                day, day, wordvec, os.path.join(region.directory, region.wordVecDir), numw)
            wordvec += tmp

        # write the total into a file for date
        f = open(outfile, 'w')
        f.write('\n'.join(['{0:.0f}'.format(x) for x in wordvec]))
        f.close()


def timeseries(start, region, useStopWindow=True):
    labMT, labMTvector, labMTwordList = emotionFileReader(
        stopval=0.0, lang=region.language, returnVector=True)
    numw = len(labMTvector)

    sumhapps = os.path.join(
        DATA_DIR,
        region.directory, region.wordVecDir,
        'sumhapps.csv'
    )
    sumfreq = os.path.join(
        DATA_DIR,
        region.directory, region.wordVecDir,
        'sumfreq.csv'
    )
    sumfile = os.path.join(
        DATA_DIR,
        region.directory, region.wordVecDir,
        start.strftime('%Y-%m-%d-sum.csv')
    )
    happsfile = os.path.join(
        DATA_DIR,
        region.directory, region.wordVecDir,
        start.strftime('%Y-%m-%d-happs.csv')
    )

    g = codecs.open(sumhapps, 'a', 'utf8')
    h = codecs.open(sumfreq, 'a', 'utf8')

    # empty array
    dayhappsarray = zeros(1)
    daywordarray = zeros(numw)

    daywordarray = genfromtxt(sumfile, dtype=float)

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
        f = codecs.open(happsfile, 'w', 'utf8')
        f.write('{0}'.format(dayhappsarray[0]))
        f.close()

        # add to main file
        g.write('{0},{1}\n'.format(
            start.strftime('%Y-%m-%d'), dayhappsarray[0]))

    # always write out the frequency
    h.write('{0},{1:.0f}\n'.format(
        start.strftime('%Y-%m-%d'), sum(daywordarray)))

    g.close()
    h.close()


def updateModel(start, region):
    # go get the database model
    t = Timeseries.objects.get(title=region.title)
    t.endDate = start
    t.save()


def preshift(start, region):
    labMT, labMTvector, labMTwordList = emotionFileReader(
        stopval=0.0, lang=region.language, returnVector=True)

    sumfile = os.path.join(
        DATA_DIR,
        region.directory, region.wordVecDir,
        start.strftime('%Y-%m-%d-sum.csv')
    )
    prevfile = os.path.join(
        DATA_DIR,
        region.directory, region.wordVecDir,
        start.strftime('%Y-%m-%d-prev7.csv')
    )
    shiftfile = os.path.join(
        DATA_DIR,
        region.directory, region.shiftDir,
        start.strftime('%Y-%m-%d-shift.csv')
    )
    metashiftfile = os.path.join(
        DATA_DIR,
        region.directory, region.shiftDir,
        start.strftime('%Y-%m-%d-metashift.csv')
    )
    word_array = genfromtxt(sumfile)
    previous_word_array = genfromtxt(prevfile)

    # compute happiness of the word vectors
    word_array_stopped = stopper(
        word_array, labMTvector, labMTwordList, ignore=IGNORE)
    previous_word_array_stopped = stopper(
        previous_word_array, labMTvector, labMTwordList, ignore=IGNORE)
    happs = emotionV(word_array_stopped, labMTvector)
    prevhapps = emotionV(previous_word_array_stopped, labMTvector)

    [sortedMag, sortedWords, sortedType, sumTypes] = shift(
        previous_word_array_stopped, word_array_stopped, labMTvector, labMTwordList)

    g = codecs.open(shiftfile, 'w', 'utf8')
    g.write("mag,word,type")
    for i in xrange(10):
        g.write("\n")
        g.write(str(sortedMag[i]))
        g.write(",")
        g.write(sortedWords[i])
        g.write(",")
        g.write(str(sortedType[i]))
    g.close()

    g = open(metashiftfile, 'w')
    g.write("refH,compH,negdown,negup,posdown,posup")
    g.write("\n{0},{1},{2},{3},{4},{5}".format(prevhapps, happs,
                                               sumTypes[0], sumTypes[1], sumTypes[2], sumTypes[3]))
    g.close()


def sort_sum_happs(region):
    sumhapps = os.path.join(
        DATA_DIR,
        region.directory, region.wordVecDir,
        'sumhapps.csv'
    )
    sumfreq = os.path.join(
        DATA_DIR,
        region.directory, region.wordVecDir,
        'sumfreq.csv'
    )
    f = open(sumhapps, 'r')
    # skip the header
    f.readline()
    dates = []
    happss = []
    for line in f:
        d, h = line.rstrip().split(',')
        date = datetime.datetime.strptime(d, '%Y-%m-%d')
        happs = float(h)
        # make sure no duplicates
        if date not in dates:
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
    f = open(sumhapps, 'w')
    f.write('date,value\n')
    for d, h in zip(dates_sorted, happss_sorted):
        f.write('{0},{1}\n'.format(d.strftime('%Y-%m-%d'), h))
    f.close()

    f = open(sumfreq, 'r')
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
            if date not in dates:
                dates.append(date)
                freqs.append(freq)
    f.close()
    # now sort
    indexer = sorted(list(range(len(dates))), key=lambda k: dates[k])
    dates_sorted = [dates[i] for i in indexer]
    freqs_sorted = [freqs[i] for i in indexer]
    f = open(sumfreq, 'w')
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


@click.command()
@click.option('--days-back', default=None)
@click.option('--start-date', default=None)
def main(days_back, start_date):
    end = datetime.datetime.now()
    end -= datetime.timedelta(hours=end.hour, minutes=end.minute,
                              seconds=end.second, microseconds=end.microsecond)

    if start_date is None and days_back is None:
        raise("Need at least some date to start from")
    if start_date is not None:
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start = end - datetime.timedelta(days=int(days_back))

    loopdates(start, end)

if __name__ == '__main__':
    main()

