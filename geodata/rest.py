# rest.py
#
# goal here is to expose function for taking two dates and adding the frequency vectors between those dates
#
# USAGE
#
# python rest.py range $(date +%Y-%m-%d -d "7 days ago") $(date +%Y-%m-%d -d "1 days ago") wordCountslastweek.csv
#
# DAY=2014-11-30
# STATE=1
# python rest.py previous ${DAY} 7 word-vectors/${STATE}/${DAY}-${STATE}-word-vector-previous7.csv ${STATE}


import copy
import datetime
import sys

import numpy


def sumfilesall(start, end, array):
    curr = copy.copy(start)
    while curr <= end:
        print("adding {0}".format(curr.strftime("%Y-%m-%d")))
        try:
            f = open("word-vectors/{0}-all-word-vector.csv".format(curr.strftime("%Y-%m-%d")), "r")
            # split into states
            tmp = f.read().split("\n")
            f.close()
            # clean to 51 states
            while len(tmp) > 51:
                del tmp[-1]
            # clean to 10222 in each state
            for i in range(51):
                tmp[i] = map(int, map(float, tmp[i].split(",")))
                while len(tmp[i]) > 10222:
                    del tmp[i][-1]

            array = array + numpy.array(tmp)

        except:
            print("could not load {0}".format(curr.strftime("%Y-%m-%d")))
            raise

        curr += datetime.timedelta(days=1)

    return array, curr


def sumfiles(start, end, array, state):
    # pass state as a string
    curr = copy.copy(start)
    while curr <= end:
        print("adding {0}".format(curr.strftime("%Y-%m-%d")))
        try:
            f = open(
                "word-vectors/{1}/{0}-{1}-word-vector.csv".format(curr.strftime("%Y-%m-%d"), state),
                "r",
            )
            # split into states
            tmp = []
            for line in f:
                # print(line)
                split_line = line.rstrip().split(",")
                # print(len(split_line))
                int_line = map(int, map(float, split_line))
                tmp.append(int_line[0:10222])
            f.close()

            # collapse if there was only one
            if len(tmp) == 1:
                tmp = tmp[0]

            array = array + numpy.array(tmp)

        except:
            print(
                "could not load word-vectors/{1}/{0}-{1}-word-vector.csv".format(
                    curr.strftime("%Y-%m-%d"), state
                )
            )
            raise

        curr += datetime.timedelta(days=1)

    return array, curr


if __name__ == "__main__":
    if sys.argv[1] == "range":
        [year, month, day] = map(int, sys.argv[2].split("-"))
        start = datetime.datetime(year, month, day)
        [year, month, day] = map(int, sys.argv[3].split("-"))
        end = datetime.datetime(year, month, day)
        outfile = sys.argv[4]

        array = numpy.zeros((51, 10222))

        [total, date] = sumfilesall(start, end, array)

        # write the total into a file for date
        print("printing to {0}".format(outfile))
        f = open(outfile, "w")
        for j in range(51):
            f.write("{0:.0f}".format(total[j][0]))
            for i in range(1, 10222):
                f.write(",{0:.0f}".format(total[j][i]))
            # don't write that last newline
            if j < 50:
                f.write("\n")
        f.close()

    if sys.argv[1] == "previous":
        [year, month, day] = map(int, sys.argv[2].split("-"))
        end = datetime.datetime(year, month, day) + datetime.timedelta(days=-1)
        start = end + datetime.timedelta(days=-int(sys.argv[3]) + 1)

        outfile = sys.argv[4]

        state = sys.argv[5]

        if state == "all":
            numstates = 51
        else:
            numstates = 1

        array = numpy.zeros((numstates, 10222))

        [total, date] = sumfiles(start, end, array, state)

        # write the total into a file for date
        print("printing to {0}".format(outfile))
        f = open(outfile, "w")
        for j in range(numstates):
            f.write("{0:.0f}".format(total[j, 0]))
            for i in range(1, 10222):
                f.write(",{0:.0f}".format(total[j, i]))
            if j < numstates - 1:
                f.write("\n")
        f.close()
