import datetime

import django
from numpy import float

django.setup()
from hedonometer.models import Timeseries, Happs  # noqa:E402 isort:skip

f = open("/usr/share/nginx/data/storywrangler_en_all/word-vectors/sumhapps.csv", "r")
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

f = open("/usr/share/nginx/data/storywrangler_en_all/word-vectors/sumfreq.csv", "r")
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

assert len(dates) == len(freqs)
assert len(dates) == len(happss)


t = Timeseries.objects.get(title="en_all")
for d, h, f in zip(dates, happss, freqs):
    h = Happs(timeseries=t, date=d, value=h, frequency=f)
    h.save()
