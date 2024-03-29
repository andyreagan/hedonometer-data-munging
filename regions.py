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
import logging
import os
import subprocess
from os import mkdir
from os.path import isdir, isfile

import click
import django
from numpy import arange, array, dot, float, vectorize, zeros

django.setup()
from hedonometer.models import Timeseries, Happs  # noqa:E402 isort:skip

DATA_DIR = "/usr/share/nginx/data"
logging.basicConfig(level=logging.INFO)


def stopper(
    tmpVec: array,
    score_list: array,
    word_list: array,
    stopVal: float = 1.0,
    ignore: list = [],
    center: float = 5.0,
):
    """Take a frequency vector, and 0 out the stop words.

    Will always remove the nig* words.

    Return the 0'ed vector."""

    ignoreWords = set(["nigga", "nigger", "niggaz", "niggas"] + ignore)
    newVec = copy.copy(tmpVec)
    newVec[abs(score_list - center) < stopVal] = 0

    def ignoreWord(word: str, ignore_set: set):
        return word in ignore_set

    ignoreWordVfun = vectorize(ignoreWord)
    newVec[ignoreWordVfun(word_list, ignoreWords)] = 0

    return newVec


def test_stopper():
    words = array(["a", "b", "c", "d"])
    ignore = ["a"]
    scores = array([-1.0, 5.0, 6.0, 7.0])
    counts = arange(4) + 10
    stopped = stopper(counts, scores, words, ignore=ignore)
    for i, count in enumerate([0, 0, 12, 13]):
        assert stopped[i] == count


def shift(refFreq: array, compFreq: array, lens: array, words: array, sort=True):
    """Compute a shift, and return the results.

    If sort=True, will return the three sorted lists, and sumTypes. Else, just the two shift lists, and sumTypes (words don't need to be sorted)."""

    # normalize frequencies
    refFreq = refFreq / refFreq.sum()
    compFreq = compFreq / compFreq.sum()

    # compute the reference happiness
    refH = dot(refFreq, lens)
    # determine shift magnitude, type
    freqDiff = compFreq - refFreq
    shiftMag = (lens - refH) * freqDiff
    shiftType = zeros(len(lens))
    shiftType[freqDiff > 0] = shiftType[freqDiff > 0] + 2
    shiftType[lens > refH] = shiftType[lens > refH] + 1

    # poor man's group_by and sum()
    sumTypes = [0.0 for i in range(4)]
    for i in range(len(lens)):
        sumTypes[int(shiftType[i])] += shiftMag[i]

    if sort:
        indices = sorted(range(len(lens)), key=lambda k: abs(shiftMag[k]), reverse=True)
        sortedMag = shiftMag[indices]
        sortedType = shiftType[indices]
        sortedWords = words[indices]
        return sortedMag, sortedWords, sortedType, sumTypes
    else:
        return shiftMag, shiftType, sumTypes


def rsync_main(region, date):
    wordvec_dir = os.path.join(DATA_DIR, region.directory, region.wordVecDir)
    logging.info(wordvec_dir)
    if not isdir(wordvec_dir):
        logging.info("creating " + wordvec_dir)
        mkdir(wordvec_dir)
    command = "rsync -avzr vacc1:{source_file} {dest_file}".format(
        source_file=os.path.join(region.sourceDir, date.strftime("%Y-%m-%d.txt")),
        dest_file=os.path.join(wordvec_dir, date.strftime("%Y-%m-%d-sum.csv")),
    )
    logging.info(command)
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
                logging.info(str(len(a)))
                logging.info(str(len(wordvec)))
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


def add_timeseries_happs(
    daywordarray: array,
    date: datetime.date,
    timeseries: Timeseries,
    score_list: array,
    total_count: int,
) -> (float, int):
    '''
    Given the counts (daywordarray) and scores (score_list),
    compute the word count, happiness, and save as a Happs object belonging
    to given timeseries object, with given date.
    '''
    freq = daywordarray.sum()
    happs = dot(daywordarray, score_list) / freq

    try:
        h = Happs.objects.get(timeseries=timeseries, date=date)
    except Happs.DoesNotExist:
        Happs(timeseries=timeseries, date=date, value=happs, frequency=total_count).save()
    else:
        h.value = happs
        h.frequency = total_count
        h.save()
 
    return happs, freq


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

    if previous_word_array_stopped.sum() == 0:
        prevhapps = 0
        sortedMag = zeros(preshift_words)
        sortedWords = array(["" for i in range(preshift_words)])
        sortedType = zeros(preshift_words)
        sumTypes = zeros(4)
    else:
        prevhapps = dot(previous_word_array_stopped, score_list) / previous_word_array_stopped.sum()
        [sortedMag, sortedWords, sortedType, sumTypes] = shift(
            refFreq=previous_word_array_stopped,
            compFreq=word_array_stopped,
            lens=score_list,
            words=word_list,
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


def process_day(
    sumfile: str,
    timeseries: Timeseries,
    currdate: datetime.date,
    numw: int,
    labMTvector: array,
    labMTwordList: array,
    ignore: list,
):
    # first time this file moved over here, check the format
    day_vector = switch_delimiter(from_delim=",", to_delim="\n", filename=sumfile)

    # add up the previous vectors
    prev7_vector = make_prev7_vector(start=currdate, region=timeseries, numw=numw)
    prev7_vector_stopped = stopper(
        tmpVec=prev7_vector, score_list=labMTvector, word_list=labMTwordList, ignore=ignore,
    )
    day_vector_stopped = stopper(
        tmpVec=day_vector, score_list=labMTvector, word_list=labMTwordList, ignore=ignore,
    )

    happs, freq = add_timeseries_happs(
        daywordarray=day_vector_stopped,
        date=currdate,
        timeseries=timeseries,
        score_list=labMTvector,
        total_count=day_vector.sum(),
    )

    preshift(
        word_array_stopped=day_vector_stopped,
        happs=happs,
        previous_word_array_stopped=prev7_vector_stopped,
        start=currdate,
        region=timeseries,
        word_list=labMTwordList,
        score_list=labMTvector,
    )

    logging.info("success")


def loopdates(
    timeseries: Timeseries, startdate: datetime.date, enddate: datetime.date, reprocess: bool
):
    currdate = copy.copy(startdate)

    labMTvector = array(timeseries.scores())
    logging.info(str(len(labMTvector)))
    logging.info(labMTvector[:5])
    logging.info(labMTvector[-5:])

    labMTwordList = array(timeseries.words())
    logging.info(str(len(labMTwordList)))
    logging.info(labMTwordList[:5])
    logging.info(labMTwordList[-5:])

    assert len(labMTvector) == len(labMTwordList)
    numw = len(labMTvector)

    ignore = timeseries.stopwords()
    logging.info(ignore)

    while currdate <= enddate:
        logging.info(
            "processing timeseries {0} on {1}".format(
                timeseries.title, datetime.datetime.strftime(currdate, "%Y-%m-%d")
            )
        )

        sumfile = os.path.join(
            DATA_DIR,
            timeseries.directory,
            timeseries.wordVecDir,
            datetime.datetime.strftime(currdate, "%Y-%m-%d-sum.csv"),
        )
        try:
            Happs.objects.get(timeseries=timeseries, date=currdate)
            # the file should exist if the previous query did,
            # but check that too
            # reprocess even if it does exist (and reprocess is true)
            if reprocess and isfile(sumfile):
                process_day(sumfile, timeseries, currdate, numw, labMTvector, labMTwordList, ignore)
        except Happs.DoesNotExist:
            logging.info("happs object not found, attempt to create it")
            
            # only attempt to pull the file if it doesn't exist
            if not isfile(sumfile):
                logging.info("file doesn't exist, trying to pull file {0} for {1}".format(timeseries.title, sumfile))
                rsync_main(region=timeseries, date=currdate)

            if isfile(sumfile):
                logging.info("file exists, doing stuff")
                process_day(sumfile, timeseries, currdate, numw, labMTvector, labMTwordList, ignore)
            else:
                logging.info("file doesn't exist: was not pulled")

        currdate += datetime.timedelta(days=1)


@click.command()
@click.option("--days-back", default="")
@click.option("--start-date", default="")
@click.option("--timeseries-title", default="")
@click.option("--reprocess", is_flag=True)
def main(days_back: str, start_date: str, timeseries_title: str, reprocess: bool):
    end = datetime.datetime.now().date()

    if (start_date == "") and (days_back == ""):
        raise ("Need at least some date to start from")
    if start_date != "":
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        start = end - datetime.timedelta(days=int(days_back))

    if timeseries_title != "":
        timeseriess = Timeseries.objects.filter(title=timeseries_title)
    else:
        timeseriess = Timeseries.objects.all()

    for timeseries in timeseriess:
        loopdates(timeseries, start, end, reprocess)


if __name__ == "__main__":
    main()
