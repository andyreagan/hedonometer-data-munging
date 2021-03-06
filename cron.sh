# this job runs from cron every hour
# check to get the most recent parsed word vector from bluemoon

# for the vacc
# cd /users/s/t/storylab/website/data/hedonometer
# for linode
echo $(date)
cd /usr/share/nginx/data

# today
# DAY=$(date +%Y-%m-%d)
# yesterday
# cron can't handle the list expansion {10..1}
# so write this out manually
for OFFSET in 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1
do
    DAY=$(date +%Y-%m-%d -d "${OFFSET} days ago")
    # some other date
    # DAY="2014-12-11"

    echo "processing $DAY"
    
    if [ ! -f word-vectors/${DAY}-sum.csv ]; then
	echo "word-vectors/${DAY}-sum.csv not found, attempting to copy"

	# may need to try both user nodes
	# echo "rsync -avzr vacc1:/users/c/d/cdanfort/scratch/twitter/daily-wordcounts/parsed.${DAY}.csv word-vectors"
	# THIS WAS THE ONE BEING USED MOST RECENTLY
	# rsync -avzr vacc2:/users/c/d/cdanfort/scratch/twitter/daily-wordcounts/parsed.${DAY}.csv word-vectors
	# rsync -avzr vacc2:/users/c/d/cdanfort/scratch/twitter/daily-wordcounts/parsed.${DAY}.csv word-vectors
	# get rid of the file
	# rm word-vectors/parsed.$(date +%Y-%m-%d).csv 

	# if [ -f word-vectors/parsed.${DAY}.csv ]; then
	    # echo "python transform10k.py parsed.${DAY}.csv"
	    # python transform10k.py parsed.${DAY}.csv

	# ...that was the old way. this is the new way (continues the if loop where that left off

	# check for, make directory to copy into
	if [ ! -d word-vectors/${DAY} ]; then
    	    mkdir "word-vectors/${DAY}"
	fi

	rsync -avzr vacc2:/users/a/r/areagan/scratch/realtime-parsing/word-vectors/${DAY}/ word-vectors/${DAY}

	python rest.py "sumday" "${DAY}" "english"
	
        if [ -f word-vectors/${DAY}-sum.csv ]; then
	    echo "python rest.py prevvectors ${DAY} ${DAY}"
	    python rest.py prevvectors ${DAY} ${DAY} english

	    echo "python timeseries.py ${DAY} ${DAY} append english"
	    python timeseries.py ${DAY} ${DAY} append english

	    echo "python preshift.py prevvectors ${DAY} ${DAY}"
	    python preshift.py ${DAY} ${DAY} english

	    . /home/prod/.env
	    echo "python addtomodel.py $(tail -n 1 word-vectors/sumhapps.csv) english"
	    python addtomodel.py $(tail -n 1 word-vectors/sumhapps.csv) english

	    /usr/local/share/phantomjs /root/phantom-crowbar/phantom-crowbar.js http://hedonometer.org/index.html?date=$(date +%Y-%m-%d -d "29 hours ago") shiftsvg /usr/share/nginx/data/screenshots/$(date +%Y-%m-%d -d "5 hours ago")/index-shift.svg
	    /usr/bin/convert /usr/share/nginx/data/screenshots/$(date +%Y-%m-%d -d "5 hours ago")/index-shift.svg /usr/share/nginx/data/screenshots/$(date +%Y-%m-%d -d "5 hours ago")/index-shift.png
	    echo "python hedotweet.py ${DAY}"
            # python hedotweet.py ${DAY}
	fi
    else
	echo "word-vectors/${DAY}-sum.csv found"
    fi
done # looping over OFFSET

# fixed the python script to save there
# mv word-vectors/${DAY}-{meta,}shift.csv shifts

# rm allhappsday.csv 
# echo "date,value" >> allhappsday.csv 
# for f in word-vectors/*sumhapps.csv; do (cat "${f}"; echo) >> allhappsday.csv; done



