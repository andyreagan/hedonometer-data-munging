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
import csv
import datetime
import os
import re
import subprocess
import sys

from labMTsimple.storyLab import *
from numpy import array, zeros

regions = [
    ["NYT", "0", "english"],
]


def processregion(region, date):
    # check the day file is there
    if not os.path.isfile(
        "/usr/share/nginx/data/word-vectors/{0}/{1}-sum.csv".format(
            region[0].lower(), datetime.datetime.strftime(date, "%Y-%m-%d")
        )
    ):
        makeSumFile(region, date)
    print(
        "checking for file /usr/share/nginx/data/word-vectors/{0}/{1}-sum.csv".format(
            region[0].lower(), datetime.datetime.strftime(date, "%Y-%m-%d")
        )
    )
    if os.path.isfile(
        "/usr/share/nginx/data/word-vectors/{0}/{1}-sum.csv".format(
            region[0].lower(), datetime.datetime.strftime(date, "%Y-%m-%d")
        )
    ):
        print("add up the previous vectors")
        rest("prevvectors", date, date, region)

        print("make timeseries")
        timeseries(date, region, useStopWindow=True)

        preshift(date, region)
    else:
        print("couldnt find the file!")
        pass


def allregions(date):
    for region in regions:
        print(
            "processing region {0} on {1}".format(
                region[0].lower(), datetime.datetime.strftime(date, "%Y-%m-%d")
            )
        )
        processregion(region, date)


def loopdates(startdate, enddate):
    while startdate <= enddate:
        allregions(startdate)
        startdate += datetime.timedelta(days=1)


def makeSumFile(region, date):
    f = open(
        "/usr/share/nginx/data/word-vectors/{0}/{1}_NYT_labVecSections.csv".format(
            region[0].lower(), datetime.datetime.strftime(date, "%Y-%m-%d")
        ),
        "r",
    )
    sections = f.readline().rstrip().split(",")
    csv_reader = csv.reader(f)
    allFreq = [map(int, row) for row in csv_reader]
    f.close()

    sumFreq = map(sum, allFreq)

    f = open(
        "/usr/share/nginx/data/word-vectors/{0}/{1}-sum.csv".format(
            region[0].lower(), datetime.datetime.strftime(date, "%Y-%m-%d")
        ),
        "w",
    )
    for i in range(len(sumFreq)):
        f.write("{0:.0f}\n".format(sumFreq[i]))
    f.close()


def rsync(region, date):
    # print("trying to get the file")
    if os.path.isdir("/usr/share/nginx/data/word-vectors/{0}".format(region[0].lower())):
        # try to get the file
        subprocess.call(
            "rsync -avzr vacc1:/users/a/r/areagan/fun/twitter/jake/pullTweets/word-vectors/{1}-{0}-word-vector.csv /usr/share/nginx/data/word-vectors/{2}/{1}-sum.csv".format(
                region[0], datetime.datetime.strftime(date, "%Y-%m-%d"), region[0].lower()
            ),
            shell=True,
        )
    else:
        os.mkdir("/usr/share/nginx/data/word-vectors/{0}".format(region[0].lower()))
        subprocess.call(
            "rsync -avzr vacc1:/users/a/r/areagan/fun/twitter/jake/pullTweets/word-vectors/{1}-{0}-word-vector.csv /usr/share/nginx/data/word-vectors/{2}/{1}-sum.csv".format(
                region[0], datetime.datetime.strftime(date, "%Y-%m-%d"), region[0].lower()
            ),
            shell=True,
        ).communicate()


def sumfiles(start, end, wordvec, lang, numw):
    curr = copy.copy(start)
    while curr <= end:
        # print("adding {0}".format(curr.strftime('%Y-%m-%d')))
        try:
            f = open(
                "/usr/share/nginx/data/word-vectors/{1}/{0}-sum.csv".format(
                    curr.strftime("%Y-%m-%d"), lang
                ),
                "r",
            )
            tmp = f.read().split("\n")
            f.close()
            while len(tmp) > numw:
                del tmp[-1]
            wordvec = wordvec + array(map(int, tmp))
        except:
            # print("could not load {0}".format(curr.strftime('%Y-%m-%d')))
            # print('could not load word-vectors/{1}/{0}-sum.csv'.format(curr.strftime('%Y-%m-%d'),lang))
            # raise
            pass
        curr += datetime.timedelta(days=1)

    return wordvec, curr


def rest(option, start, end, region, outfile="test.csv", days=[]):
    # if the option is range, pass it an outfile to write to
    # if the option is list, pass it an outfile and days list
    if option == "prevvectors":
        labMT, labMTvector, labMTwordList = emotionFileReader(
            stopval=0.0, fileName="labMT2" + region[2] + ".txt", returnVector=True
        )
        numw = len(labMTvector)

        maincurr = copy.copy(start + datetime.timedelta(days=-1))
        while maincurr < end:
            wordvec = zeros(numw)
            # added the try loop to handle failure inside the sumfiles
            # try:
            [total, date] = sumfiles(
                maincurr + datetime.timedelta(days=-6),
                maincurr + datetime.timedelta(days=0),
                wordvec,
                region[0].lower(),
                numw,
            )

            # write the total into a file for date
            # print("printing to {0}-prev7.csv".format(date.strftime('%Y-%m-%d')))
            f = open(
                "/usr/share/nginx/data/word-vectors/{1}/{0}-prev7.csv".format(
                    date.strftime("%Y-%m-%d"), region[0].lower()
                ),
                "w",
            )
            for i in range(numw):
                f.write("{0:.0f}\n".format(total[i]))
            f.close()
            # except:
            #     print("failed on {0}".format(date.strftime('%Y-%m-%d')))
            #     print("-------------------------------")
            maincurr += datetime.timedelta(days=1)

    if option == "range":
        labMT, labMTvector, labMTwordList = emotionFileReader(
            stopval=0.0, fileName="labMT2" + region[2] + ".txt", returnVector=True
        )
        numw = len(labMTvector)

        wordvec = zeros(numw)

        [total, date] = sumfiles(start, end, wordvec, region[0].lower(), numw)

        # write the total into a file for date
        # print("printing to {0}".format(date.strftime('%Y-%m-%d')))
        f = open(outfile, "w")
        for i in range(numw):
            f.write("{0}\n".format(total[i]))
        f.close()
        # except:
        #     print("failed on {0}".format(date.strftime('%Y-%m-%d')))
        #     print("-------------------------------")

    if option == "list":
        # print("heads up, the second word after list needs to be the language")
        labMT, labMTvector, labMTwordList = emotionFileReader(
            stopval=0.0, fileName="labMT2" + region[2] + ".txt", returnVector=True
        )
        numw = len(labMTvector)

        wordvec = zeros(numw)
        for day in days:
            # this should handle the array object by reference
            [tmp, date] = sumfiles(day, day, wordvec, region[0].lower(), numw)
            wordvec += tmp

        # write the total into a file for date
        # print("printing to {0}".format(outfile))
        f = open(outfile, "w")
        for i in range(numw):
            f.write("{0:.0f}\n".format(wordvec[i]))
        f.close()


def timeseries(start, region, useStopWindow=True):
    labMT, labMTvector, labMTwordList = emotionFileReader(
        stopval=0.0, fileName="labMT2" + region[2] + ".txt", returnVector=True
    )
    numw = len(labMTvector)

    # print("opening in append mode"        )
    g = codecs.open(
        "/usr/share/nginx/data/word-vectors/" + region[0].lower() + "/sumhapps.csv", "a", "utf8"
    )
    h = codecs.open(
        "/usr/share/nginx/data/word-vectors/" + region[0].lower() + "/sumfreq.csv", "a", "utf8"
    )

    # loop over time
    currDay = copy.copy(start)

    # empty array
    happsarray = zeros(24)
    dayhappsarray = zeros(1)
    wordarray = [zeros(numw) for i in range(24)]
    daywordarray = zeros(numw)

    # print('reading word-vectors/'+region[0].lower()+'/{0}'.format(currDay.strftime('%Y-%m-%d-sum.csv')))

    # try
    f = codecs.open(
        "/usr/share/nginx/data/word-vectors/"
        + region[0].lower()
        + "/{0}-sum.csv".format(currDay.strftime("%Y-%m-%d")),
        "r",
        "utf8",
    )
    daywordarray = array(map(float, f.read().split("\n")[0:numw]))
    f.close()
    # print(daywordarray)
    print(len(daywordarray))
    # compute happiness of the word vectors
    if useStopWindow:
        stoppedVec = stopper(
            daywordarray,
            labMTvector,
            labMTwordList,
            ignore=["thirsty", "pakistan", "india", "nigga", "niggaz", "niggas", "nigger"],
        )
        happs = emotionV(stoppedVec, labMTvector)
    else:
        happs = emotionV(daywordarray, labMTvector)
    dayhappsarray[0] = happs

    if dayhappsarray[0] > 0:
        # write out the day happs
        # print('writing word-vectors/{1}/{0}-happs'.format(currDay.strftime('%Y-%m-%d'),region[0].lower()))
        f = codecs.open(
            "/usr/share/nginx/data/word-vectors/{1}/{0}-happs.csv".format(
                currDay.strftime("%Y-%m-%d"), region[0].lower()
            ),
            "w",
            "utf8",
        )
        f.write("{0}".format(dayhappsarray[0]))
        f.close()

        # add to main file
        g.write("{0},{1}\n".format(currDay.strftime("%Y-%m-%d"), dayhappsarray[0]))

    # always write out the frequency
    h.write("{0},{1:.0f}\n".format(currDay.strftime("%Y-%m-%d"), sum(daywordarray)))

    g.close()
    h.close()


def preshift(start, region):
    labMT, labMTvector, labMTwordList = emotionFileReader(
        stopval=0.0, fileName="labMT2" + region[2] + ".txt", returnVector=True
    )
    numw = len(labMTvector)

    # loop over time
    currDay = copy.copy(start)

    # empty array
    wordarray = zeros(numw)
    prevwordarray = zeros(numw)

    # print('reading word-vectors/{1}/{0}'.format(currDay.strftime('%Y-%m-%d-sum.csv'),region[0].lower()))
    f = codecs.open(
        "/usr/share/nginx/data/word-vectors/{1}/{0}-sum.csv".format(
            currDay.strftime("%Y-%m-%d"), region[0].lower()
        ),
        "r",
        "utf8",
    )
    wordarray = array(map(float, f.read().split("\n")[0:numw]))
    f.close()

    # print('reading word-vectors/{1}/{0}'.format(currDay.strftime('%Y-%m-%d-prev7.csv'),region[0].lower()))
    f = codecs.open(
        "/usr/share/nginx/data/word-vectors/{1}/{0}-prev7.csv".format(
            currDay.strftime("%Y-%m-%d"), region[0].lower()
        ),
        "r",
        "utf8",
    )
    prevwordarray = array(map(float, f.read().split("\n")[0:numw]))
    f.close()

    # print(daywordarray)
    # print(len(wordarray))
    # print(len(prevwordarray))

    if sum(prevwordarray) > 0:
        # compute happiness of the word vectors
        wordarrayst = stopper(
            wordarray,
            labMTvector,
            labMTwordList,
            ignore=["thirsty", "pakistan", "india", "nigga", "niggas", "niggaz", "nigger"],
        )
        prevwordarrayst = stopper(
            prevwordarray,
            labMTvector,
            labMTwordList,
            ignore=["thirsty", "pakistan", "india", "nigga", "niggas", "niggaz", "nigger"],
        )
        happs = emotionV(wordarrayst, labMTvector)
        prevhapps = emotionV(prevwordarrayst, labMTvector)
        # print(happs)

        [sortedMag, sortedWords, sortedType, sumTypes] = shift(
            prevwordarrayst, wordarrayst, labMTvector, labMTwordList
        )
        # print(sortedMag[:10])
        # print(sortedWords[:10])
        # print(sortedType[:10])
        # print(sumTypes)

        # print('writing /usr/share/nginx/data/shifts/{1}/{0}-shift.csv'.format(currDay.strftime('%Y-%m-%d'),region[0].lower()))
        g = codecs.open(
            "/usr/share/nginx/data/shifts/{1}/{0}-shift.csv".format(
                currDay.strftime("%Y-%m-%d"), region[0].lower()
            ),
            "w",
            "utf8",
        )
        g.write("mag,word,type")
        for i in range(10):
            g.write("\n")
            g.write(str(sortedMag[i]))
            g.write(",")
            g.write(sortedWords[i])
            g.write(",")
            g.write(str(sortedType[i]))
        g.close()

        # print('writing /usr/share/nginx/data/shifts/{1}/{0}-metashift.csv'.format(currDay.strftime('%Y-%m-%d'),region[0].lower()))
        g = open(
            "/usr/share/nginx/data/shifts/{1}/{0}-metashift.csv".format(
                currDay.strftime("%Y-%m-%d"), region[0].lower()
            ),
            "w",
        )
        g.write("refH,compH,negdown,negup,posdown,posup")
        g.write(
            "\n{0},{1},{2},{3},{4},{5}".format(
                prevhapps, happs, sumTypes[0], sumTypes[1], sumTypes[2], sumTypes[3]
            )
        )
        g.close()
    else:
        print("previous word vector empty")


def makeshiftdirectories():
    for region in regions:
        os.mkdir("/usr/share/nginx/data/shifts/{0}".format(region[0].lower()))


def emptysumhapps():
    for region in regions:
        f = open(
            "/usr/share/nginx/data/word-vectors/{0}/sumhapps.csv".format(region[0].lower()), "w"
        )
        f.write("date,value\n")
        f.close()
        f = open(
            "/usr/share/nginx/data/word-vectors/{0}/sumfreq.csv".format(region[0].lower()), "w"
        )
        f.write("date,value\n")
        f.close()


def printlinks():
    for region in regions:
        print("http://hedonometer.org/{0}/".format(region[0].lower()))


if __name__ == "__main__":

    # makeshiftdirectories()

    # emptysumhapps()

    # printlinks()

    # do the rsync
    # start = datetime.datetime(2014,4,15)
    # start = datetime.datetime(2007,6,15)
    start = datetime.datetime(1987, 1, 1)
    # start = datetime.datetime.now() - datetime.timedelta(days=10)
    end = datetime.datetime(2007, 6, 19)
    # end = datetime.datetime.now()

    loopdates(start, end)
