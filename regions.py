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

import copy
import datetime
import os
import subprocess
from os import mkdir
from os.path import isdir, isfile

import click
import django
from labMTsimple.storyLab import emotionV, shift, stopper
from numpy import array, float, sum, zeros

django.setup()
from hedonometer.models import Timeseries, Happs  # noqa:E402 isort:skip

DATA_DIR = "/usr/share/nginx/data"
with open(os.path.join(DATA_DIR, Timeseries.objects.all()[0].directory, "stopwords.csv"), "r") as f:
    IGNORE = f.read().split("\n")


def rsync_main(region, date):
    wordvec_dir = os.path.join(DATA_DIR, region.directory, region.wordVecDir)
    print(wordvec_dir)
    if not isdir(wordvec_dir):
        print("creating", wordvec_dir)
        mkdir(wordvec_dir)
    command = "rsync -avzr vacc2:{source_file} {dest_file}".format(
        source_file=os.path.join(region.sourceDir, date.strftime("%Y-%m-%d.txt")),
        dest_file=os.path.join(wordvec_dir, date.strftime("%Y-%m-%d-sum.csv")),
    )
    print(command)
    subprocess.call(command, shell=True)


def sumfiles(start, end, wordvec, title):
    """start: start date
    end: end date
    wordvec: numpy array
    title: folder to load from

    loads each file, inclusive of the start and end"""

    curr = copy.copy(start)
    files = {}
    while curr <= end:
        sumfile = os.path.join(DATA_DIR, title, curr.strftime("%Y-%m-%d-sum.csv"))
        if os.path.isfile(sumfile):
            # switch_delimiter(',', '\n', sumfile)
            with open(sumfile, "r") as f:
                a = array(list(map(float, f.read().strip().split())))
            if len(a) != len(wordvec):
                print(len(a))
                print(len(wordvec))
            assert len(a) == len(wordvec)
            wordvec = wordvec + a
            files[curr] = a
        curr += datetime.timedelta(days=1)

    return wordvec, files


def make_prev7_vector(start, region, numw):
    """This reads word vector files from disk and writes them to an output file.

    start: start date, datetime.date
    region: the Timeseries object
    numw: number of words to expect
    """

    total, wordvecs = sumfiles(
        start + datetime.timedelta(days=-7),
        start + datetime.timedelta(days=-1),
        zeros(numw),
        os.path.join(region.directory, region.wordVecDir),
    )

    sumfilename = os.path.join(
        DATA_DIR, region.directory, region.wordVecDir, start.strftime("%Y-%m-%d-prev7.csv")
    )
    # write the total into a file for date
    with open(sumfilename, "w") as f:
        f.write("\n".join(["{0:.0f}".format(x) for x in total]))

    return total


def timeseries(daywordarray, date, region, word_list, score_list, useStopWindow=True):
    sumhapps = os.path.join(DATA_DIR, region.directory, region.wordVecDir, "sumhapps.csv")
    sumfreq = os.path.join(DATA_DIR, region.directory, region.wordVecDir, "sumfreq.csv")
    happsfile = os.path.join(
        DATA_DIR, region.directory, region.wordVecDir, date.strftime("%Y-%m-%d-happs.csv")
    )

    # compute happiness of the word vectors
    if useStopWindow:
        stoppedVec = stopper(
            tmpVec=daywordarray, score_list=score_list, word_list=word_list, ignore=IGNORE
        )
    else:
        stoppedVec = daywordarray

    happs = emotionV(stoppedVec, score_list)

    if happs > 0:
        # write out the day happs
        with open(happsfile, "w") as f:
            f.write("{0}".format(happs))

        # add to main file
        with open(sumhapps, "a") as g:
            g.write("{0},{1}\n".format(date.strftime("%Y-%m-%d"), happs))

        Happs.objects.filter(timeseries=region, date=date).delete()
        Happs(timeseries=region, date=date, value=happs, frequency=sum(daywordarray))

    # always write out the frequency
    with open(sumfreq, "a") as h:
        h.write("{0},{1:.0f}\n".format(date.strftime("%Y-%m-%d"), sum(daywordarray)))

    return stoppedVec, happs, sum(daywordarray)


def updateModel(start, region):
    # go get the database model
    t = Timeseries.objects.get(title=region.title)
    t.endDate = start
    t.save()


def preshift(
    word_array_stopped,
    happs,
    previous_word_array_stopped,
    start,
    region,
    word_list,
    score_list,
    preshift_words=10,
):
    shiftfile = os.path.join(
        DATA_DIR, region.directory, region.shiftDir, start.strftime("%Y-%m-%d-shift.csv")
    )
    metashiftfile = os.path.join(
        DATA_DIR, region.directory, region.shiftDir, start.strftime("%Y-%m-%d-metashift.csv")
    )

    if sum(previous_word_array_stopped) == 0:
        prevhapps = 0
        sortedMag = zeros(preshift_words)
        sortedWords = array(["" for i in range(preshift_words)])
        sortedType = zeros(preshift_words)
        sumTypes = zeros(4)
    else:
        prevhapps = emotionV(previous_word_array_stopped, score_list)
        [sortedMag, sortedWords, sortedType, sumTypes] = shift(
            previous_word_array_stopped, word_array_stopped, score_list, word_list
        )

    with open(shiftfile, "w") as g:
        g.write("mag,word,type")
        for i in range(preshift_words):
            g.write("\n")
            g.write(str(sortedMag[i]))
            g.write(",")
            g.write(sortedWords[i])
            g.write(",")
            g.write(str(sortedType[i]))

    with open(metashiftfile, "w") as g:
        g.write("refH,compH,negdown,negup,posdown,posup")
        g.write(
            "\n{0},{1},{2},{3},{4},{5}".format(
                prevhapps, happs, sumTypes[0], sumTypes[1], sumTypes[2], sumTypes[3]
            )
        )
    return prevhapps, sortedMag, sortedWords, sortedType, sumTypes


def sort_sum_happs(region):
    sumhapps = os.path.join(DATA_DIR, region.directory, region.wordVecDir, "sumhapps.csv")
    sumfreq = os.path.join(DATA_DIR, region.directory, region.wordVecDir, "sumfreq.csv")
    f = open(sumhapps, "r")
    # skip the header
    f.readline()
    dates = []
    happss = []
    for line in f:
        d, h = line.rstrip().split(",")
        date = datetime.datetime.strptime(d, "%Y-%m-%d")
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
    f = open(sumhapps, "w")
    f.write("date,value\n")
    for d, h in zip(dates_sorted, happss_sorted):
        f.write("{0},{1}\n".format(d.strftime("%Y-%m-%d"), h))
    f.close()

    f = open(sumfreq, "r")
    # skip the header
    f.readline()
    dates = []
    freqs = []
    for line in f:
        tmp = line.rstrip().split(",")
        if len(tmp) == 2:
            d, fr = tmp
            date = datetime.datetime.strptime(d, "%Y-%m-%d")
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
    f = open(sumfreq, "w")
    f.write("date,value\n")
    for d, fr in zip(dates_sorted, freqs_sorted):
        f.write("{0},{1:.0f}\n".format(d.strftime("%Y-%m-%d"), fr))
    f.close()


def switch_delimiter(from_delim: str, to_delim: str, filename: str) -> array:
    # switch_delimiter(from_delim,to_delim,filename)
    #
    # attempt to swith the delimiter of a file, safely
    # tested briefly on the `realtime-parse` data
    with open(filename, "r") as f:
        raw = f.read()

    if from_delim in raw:
        my_array = list(map(lambda x: int(float(x)), raw.rstrip(from_delim).split(from_delim)))
        with open(filename, "w") as f:
            f.write(to_delim.join(["{0:.0f}".format(x) for x in my_array]))
        return array(my_array)
    else:
        return array(list(map(lambda x: int(float(x)), raw.rstrip(to_delim).split(to_delim))))


def loopdates(startdate, enddate):
    for region in Timeseries.objects.all():
        currdate = copy.copy(startdate)
        while currdate <= enddate:
            print(
                "processing region {0} on {1}".format(
                    region.title, datetime.datetime.strftime(currdate, "%Y-%m-%d")
                )
            )
            with open(os.path.join(DATA_DIR, region.directory, region.scoreList), "r") as f:
                labMTvector = list(map(float, f.read().strip().split("\n")))
            print(len(labMTvector))
            with open(os.path.join(DATA_DIR, region.directory, region.wordList), "r") as f:
                labMTwordList = f.read().strip().split("\n")
            print(len(labMTwordList))

            assert len(labMTvector) == len(labMTwordList)
            numw = len(labMTvector)

            sumfile = os.path.join(
                DATA_DIR,
                region.directory,
                region.wordVecDir,
                datetime.datetime.strftime(currdate, "%Y-%m-%d-sum.csv"),
            )
            if not isfile(sumfile):
                print("trying to pull file {0} for {1}".format(region.title, sumfile))
                rsync_main(region, currdate)

                if isfile(sumfile):
                    print("file was pulled, doing stuff")

                    # first time this file moved over here, check the format
                    day_vector = switch_delimiter(",", "\n", sumfile)

                    # add up the previous vectors
                    prev7_vector = make_prev7_vector(currdate, region, numw)
                    prev7_vector_stopped = stopper(
                        tmpVec=prev7_vector,
                        score_list=labMTvector,
                        word_list=labMTwordList,
                        ignore=IGNORE,
                    )

                    day_vector_stopped, happs, freq = timeseries(
                        day_vector,
                        currdate,
                        region,
                        word_list=labMTwordList,
                        score_list=labMTvector,
                        useStopWindow=True,
                    )

                    preshift(
                        day_vector_stopped,
                        happs,
                        prev7_vector_stopped,
                        currdate,
                        region,
                        word_list=labMTwordList,
                        score_list=labMTvector,
                    )

                    # updateModel(currdate, region)
                    print("success")

            currdate += datetime.timedelta(days=1)
        sort_sum_happs(region)


@click.command()
@click.option("--days-back", default=None)
@click.option("--start-date", default=None)
def main(days_back, start_date):
    end = datetime.datetime.now()
    end -= datetime.timedelta(
        hours=end.hour, minutes=end.minute, seconds=end.second, microseconds=end.microsecond
    )

    if start_date is None and days_back is None:
        raise ("Need at least some date to start from")
    if start_date is not None:
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start = end - datetime.timedelta(days=int(days_back))

    loopdates(start, end)


if __name__ == "__main__":
    main()
