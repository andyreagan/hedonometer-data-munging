import sys, os
sys.path.append('/home/prod/hedonometer')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','mysite.settings')
from django.conf import settings

from hedonometer.models import Actor,Director,Writer,Movie

import unirest
import datetime

def loop():
    f = open("titles-clean.txt","r")
    titles = [line.rstrip() for line in f]
    f.close()
    f = open("titles-raw.txt","r")
    rawtitles = [line.rstrip() for line in f]
    f.close()

    g = open("noresult.txt","a")
    
    startat = 1083
    endat = 1100
    
    for i in xrange(startat,endat):
        title = titles[i]
        rawtitle = rawtitles[i]
        scrape(title,rawtitle,g)

    f.close()
    g.close()

def scrape(title,rawtitle,g):
    print "-"*80
    print "-"*80
    print title
    print "-"*80

    response = unirest.post("https://imdb.p.mashape.com/movie",
                            headers={
                                # "X-Mashape-Key": "KZE1CO4Mn7mshjabQzICrvp0grcSp1P4tgfjsnMW4yBZK1vhU7",
                                "X-Mashape-Key": "KZE1CO4Mn7mshjabQzICrvp0grcSp1P4tgfjsnMW4yBZK1vhU7",
                                "Content-Type": "application/x-www-form-urlencoded",
                            },
                                params={
                                    "searchTerm": title,
                                })

    print response.body

    if response.body["success"] in [True,"true","True"]:
        print response.body["result"]

        print "-"*80
        print "actors:"
        # go get, or create, all the actor models
        actor_list = []
        for actor in response.body["result"]["cast"]:
            name = actor["actor"]
            print name
            q = Actor.objects.filter(name__exact=name)
            if len(q) > 0:
                a = q[0]
            else:
                a = Actor(name=name)
                a.save()

            actor_list.append(a)

        print "-"*80
        print "directors:"
        director_list = []
        if isinstance(response.body["result"]["director"], basestring):
            directors = [response.body["result"]["director"]]
        else:
            directors = response.body["result"]["director"]
        for director in directors:
            name = director
            print name
            q = Director.objects.filter(name__exact=name)
            if len(q) > 0:
                a = q[0]
            else:
                a = Director(name=name)
                a.save()

            director_list.append(a)

        print "-"*80
        print "writers:"
        writer_list = []
        if isinstance(response.body["result"]["writer"], basestring):
            writers = [response.body["result"]["writer"]]
        else:
            writers = response.body["result"]["writer"]
        for writer in writers:
            name = writer
            print name
            q = Writer.objects.filter(name__exact=name)
            if len(q) > 0:
                a = q[0]
            else:
                a = Writer(name=name)
                a.save()
            writer_list.append(a)
                
        genre = ",".join(response.body["result"].get("genre","none"))
        keywords = ",".join(response.body["result"].get("keywords","none"))
        language = response.body["result"].get("language","none")
        imdbid = response.body["result"].get("id","none")
        metascore = response.body["result"]["metascore"].get("given","none")
        image = response.body["result"].get("poster","none")
        rating = response.body["result"]["rating"].get("content","none")
        date1 = response.body["result"].get("releaseDate","Thu Nov 20 2014")
        if date1 == "Invalid Date":
            date1 = "Thu Nov 20 2014"
        releaseDate = datetime.datetime.strptime(date1,"%a %b %d %Y") # Fri Nov 21 2008
        reviews = response.body["result"]["reviews"].get("user","none")
        runtime = response.body["result"].get("runtime","none")
        storyline = response.body["result"].get("storyline","none")
        year = response.body["result"].get("year","none")

        m = Movie(
            filename = title.replace(" ","-"),
            title = title,
            rawtitle = rawtitle,
            # director = director_list,
            # actor = actor_list,
            # writer = writer_list,
            language = language,
            happs = 0.0,
            length = "0",
            ignorewords = "nigg",
            wiki = "nolink",
            image = image,
            genre = genre,
            imdbid = imdbid,
            keywords = keywords,
            metascore = metascore,
            rating = rating,
            releaseDate = releaseDate,
            reviews = reviews,
            runtime = runtime,
            storyline=storyline,
            year=year,
        )
        m.save()
        for d in director_list:
            m.director.add(d)
        for d in actor_list:
            m.actor.add(d)
        for d in writer_list:
            m.writer.add(d)
        m.save()
    else:
        g.write(title)
        g.write("\n")

if __name__ == "__main__":
    scrape()








