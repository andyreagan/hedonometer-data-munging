# txttowordvec.py
#
# take a text file, write out the word vector
#
# USAGE
#
# python txttowordvec.py -o outfile.csv -i infile.txt -l english
# if no in, or out file, will use stdin/stdout

import sys

from labMTsimple.storyLab import *


def chop(f, g, labMT, labMTvector):
    rawtext = f.read()
    print(len(rawtext))
    textValence, textFvec = emotion(rawtext, labMT, shift=True, happsList=labMTvector)
    f.close()

    sep = ","

    g.write("{0:.0f}".format(textFvec[0]))
    for i in range(1, len(labMTvector)):
        g.write("{1}{0:.0f}".format(textFvec[i], sep))
    g.close()


if __name__ == "__main__":
    infstream = sys.stdin
    outfstream = sys.stdout
    lang = "english"

    for i in range(len(sys.argv)):
        arg = sys.argv[i]
        if arg == "-o":
            print("using a file as outfstream")
            outfstream = open(sys.argv[i + 1], "w")
        if arg == "-i":
            print("using a file as infstream")
            infstream = open(sys.argv[i + 1], "r")
        if arg == "-l":
            lang = sys.argv[i + 1]

    labMT, labMTvector, labMTwordList = emotionFileReader(stopval=0.0, lang=lang, returnVector=True)

    chop(infstream, outfstream, labMT, labMTvector)
