# chop.py
#
# chop up a text into a bunch of frequency vectors of length
#
# USAGE
#
# python chop.py data/count-of-monte-cristo.txt output french

import codecs  # handle utf8
import re
import sys  # for user inpurt

from django.conf import settings
from hedonometer.models import Book
from labMTsimple.storyLab import *

sys.path.append("/home/prod/app")
os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings"


def chopper(words, labMT, labMTvector, outfile, minSize=1000):
    # print("now splitting the text into chunks of size 1000")
    # print("and printing those frequency vectors")
    allFvec = []
    from numpy import floor

    for i in range(int(floor(len(words) / minSize))):
        chunk = unicode("")
        if i == int(floor(len(words) / minSize)) - 1:
            # take the rest
            for j in range(i * minSize, len(words) - 1):
                chunk += words[j] + unicode(" ")
        else:
            for j in range(i * minSize, (i + 1) * minSize):
                chunk += words[j] + unicode(" ")

        textValence, textFvec = emotion(chunk, labMT, shift=True, happsList=labMTvector)
        allFvec.append(textFvec)

    print("writing out the file to {0}".format(outfile))
    f = open("processed/" + outfile + ".csv", "w")
    f.write("{0:.0f}".format(allFvec[0][0]))
    for k in range(1, len(allFvec)):
        f.write(",{0:.0f}".format(allFvec[k][0]))
    for i in range(1, len(allFvec[0])):
        f.write("\n")
        f.write("{0:.0f}".format(allFvec[0][i]))
        for k in range(1, len(allFvec)):
            f.write(",{0:.0f}".format(allFvec[k][i]))
    f.close()

    # print("done!")


if __name__ == "__main__":
    rawbook, saveas, lang, author, title = sys.argv[1:]

    labMT, labMTvector, labMTwordList = emotionFileReader(stopval=0.0, lang=lang, returnVector=True)

    # f = codecs.open(rawbook,"r","utf8")
    f = open(rawbook, "r")
    raw_text = f.read()
    f.close()

    words = [
        x.lower() for x in re.findall(r"[\w\@\#\'\&\]\*\-\/\[\=\;]+", raw_text, flags=re.UNICODE)
    ]

    randomize = False

    if randomize:
        from random import shuffle

        shuffle(words)

    chopper(words, labMT, labMTvector, saveas)

    avhapps = emotion(raw_text, labMT)

    b = Book(
        filename=saveas, title=title, author=author, language=lang, happs=avhapps, length=len(words)
    )
    b.save()
