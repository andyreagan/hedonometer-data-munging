# from sys import path
# path.append("/Users/andyreagan/tools/python")
# from labMTsimple.labMTsimple.storyLab import stopper,emotionV
# from labMTsimple.labMTsimple.speedy import LabMT
# my_LabMT = LabMT()
from sys import argv

# import numpy as np
from numpy import array, cumsum, dot, floor, genfromtxt, sum, zeros

if __name__ == "__main__":
    word_vecs = [genfromtxt(f) for f in argv[1:-1]]
    all_vecs = zeros(len(word_vecs[0]))
    for v in word_vecs:
        all_vecs += v
    f = open(argv[-1], "w")
    f.write("\n".join(list(map(lambda x: "{0:.0f}".format(x), all_vecs))))
    f.close()
