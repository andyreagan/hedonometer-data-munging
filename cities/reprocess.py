import re
from copy import copy
from labMTsimple.storyLab import *
from sys import argv

ignore = ["nigga", "niggas", "niggaz", "nigger","thirsty","pakistan","india", "severe", "flood", "warning", "earthquake", "humidity", "pressure", "burns", "emergency", "grand", "springs", "falls", "battle", "old", "miami","pearl", "santa", "atlantic", "grand", "green", "falls", "lake", "haven", "sin", "con", "war","mercy","gren","beach","bills","health","springfield","falling","international","terminal","mad", "al","ak","az","ar","ca","co","ct","de","fl","ga","hi","id","il","in","ia","ks","ky","la","me","md","ma","mi","mn","ms","mo","mt","ne","nv","nh","nj","nm","ny","nc","nd","oh","ok","or","pa","ri","sc","sd","tn","tx","ut","vt","va","wa","wv","wi","wy", "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "new", "hampshire", "jersey", "mexico", "york", "north", "carolina", "dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode", "island", "south", "carolina", "dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington", "west", "virginia", "wisconsin",]

lang = "english"
labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+lang+'.txt',returnVector=True)

def subset(data):
    allSets = [set() for year in years]
    i = 0
    for year in years:
        for city in data[year]: # keys from the dict
            allSets[i].add(city)
        i += 1

    subset = copy(allSets[0])
    for i in xrange(len(years)):
        subset = subset.intersection(allSets[i])

    return subset

def reprocessyears(allData,endfix):

    print len(allData)
    print allData[0]
    print allData[-1]

    years = range(2011,2015)

    for year in years:
        print year
        if year < 2014:
            pre2014 = ".new"
        else:
            pre2014 = ""
        if year == 2011:
            year = "2011_PLOS"
        for i in xrange(len(allData)):
            print i
            city = allData[i][0]
            g = open("word-vectors/"+str(year)+"/"+city+".csv"+pre2014,"r")
            fvec = map(int,g.readline().split(","))
            g.close()
            svec = stopper(fvec,labMTvector,labMTwordList,ignore=ignore)
            happs = emotionV(svec,labMTvector)
            allData[i].append(happs)
            
    
    for i in xrange(len(years)):
        g = open("cityList_"+str(years[i])+"_"+endfix+"Happs.csv","w")
        for j in xrange(len(allData)):
            g.write('{0:.8f}'.format(allData[j][i+1]))
            g.write("\n")
        g.close()

def cityhapps(city,year):

    if int(year) < 2014:
        pre2014 = ".new"
    else:
        pre2014 = ""
    g = open("word-vectors/"+str(year)+"/"+city+".csv"+pre2014,"r")
    fvec = map(int,g.readline().split(","))
    g.close()
    svec = stopper(fvec,labMTvector,labMTwordList,ignore=ignore)
    happs = emotionV(svec,labMTvector)
    
    return happs

if __name__ == '__main__':
    
    tmp = argv[1]
    if tmp == "PLOS":
        f = open("mutualCities.csv","r")
        allData = [[re.sub('--','-',line).rstrip()] for line in f]
        f.close()
        reprocessyears(allData,"PLOS")
    if tmp == "PLOS-really":
        # the 2011 list...but don't have all the word vectors
        print "this won't work"
        f = open("PLOS_cities_nocsv.csv","r")
        allData = [[re.sub('--','-',line).rstrip()] for line in f]
        f.close()
        reprocessyears(allData,"PLOS")
    if tmp == "top100":        
        f = open("2014top100.csv","r")
        allData = [[re.sub('--','-',",".join(line.split(",")[1:])).rstrip()] for line in f]
        f.close()
        reprocessyears(allData,"top100")
    if tmp == "city":
        city = argv[2]
        year = argv[3]
        happs = cityhapps(city,year)
        print "{0} in {1} had happiness of {2:.5f}".format(city,year,happs)
        
    

                    
        


    









