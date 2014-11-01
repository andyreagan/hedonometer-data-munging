import re
from copy import copy

# to upgrade for 2014, just add it here
years = ['2011','2012','2013','2014']

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

if __name__ == '__main__':

    allData = dict()
    
    for year in years:
    
        f = open("cityList_"+year+".csv","r")
        g = open("cityList_"+year+"_justCities.csv","w")
        h = open("cityList_"+year+"_justHapps.csv","w")
    
        allData[year] = dict()
        for line in f:
            city = re.sub('--','-',",".join(line.rstrip().split(",")[0:-1])[1:-1])
            happs = line.rstrip().split(",")[-1]
            allData[year][city] = happs
            g.write(city)
            g.write("\n")
            h.write(happs)
            h.write("\n")
        
        f.close()
        g.close()
        h.close()

    citySet = subset(allData)
    
    # print citySet
    print len(citySet)
    
    # fix the city set
    cityList = [city for city in citySet]

    # write out the fixed set of cities
    f = open("mutualCities.csv","w")
    for city in cityList:
        f.write(city)
        f.write("\n")
    f.close()

    # print allData

    for year in years:
        g = open("cityList_"+year+"_mutualHapps.csv","w")
        for city in cityList:
            g.write(allData[year][city])
            g.write("\n")
        g.close()
                    
        


    









