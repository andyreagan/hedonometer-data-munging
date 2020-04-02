import datetime
import json
from sys import argv

from twython import Twython, TwythonError
from urllib2 import Request, URLError, urlopen


def tweetit(text):

    # store the keys somewhere (so I can share this script)
    f = open("hedostatuskeys", "r")
    APP_KEY = f.readline().rstrip()
    print(APP_KEY)
    APP_SECRET = f.readline().rstrip()
    print(APP_SECRET)
    OAUTH_TOKEN = f.readline().rstrip()
    print(OAUTH_TOKEN)
    OAUTH_TOKEN_SECRET = f.readline().rstrip()
    print(OAUTH_TOKEN_SECRET)
    f.close()

    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    try:
        twitter.update_status(status=text)
    except TwythonError as e:
        print(e)


if __name__ == "__main__":

    d = argv[1]
    date = datetime.datetime.strptime(d, "%Y-%m-%d")
    print(date)

    rurl = "http://hedonometer.org/api/v1/timeseries/?format=json&date={0}".format(
        date.strftime("%Y-%m-%d")
    )
    request = Request(rurl)

    print(rurl)

    try:
        response = urlopen(request)
        tmp = response.read()
        print(tmp)
        tmp = json.loads(tmp)
        print(tmp)
        print(len(tmp["objects"]))
        if len(tmp["objects"]) < 1:
            print("tweeting to andyreagan")
            tweetit("@andyreagan my api is not up to date: {0}".format(rurl))
        else:
            print("were okay")
    except URLError as e:
        tweet = "error from {0}".format(rurl)
        print(tweet)
