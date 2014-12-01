# this job runs from cron every hour
# check to get the most recent parsed word vector from bluemoon

LANG=$1

# for the vacc
# cd /users/s/t/storylab/website/data/hedonometer
# for linode
echo $(date)
cd /usr/share/nginx/data

# today
# DAY=$(date +%Y-%m-%d)
# yesterday
DAY=$(date +%Y-%m-%d -d "29 hours ago")
# some other date
# DAY="2014-10-31"

echo "processing ${DAY} for ${LANG}"

if [ ! -f word-vectors/${LANG}/${DAY}-sum.csv ]; then
    echo "word-vectors/parsed.${DAY}.csv not found, attempting to copy"

    # may need to try both user nodes
    # echo "rsync -avzr vacc1:/users/c/d/cdanfort/scratch/twitter/daily-wordcounts/parsed.${DAY}.csv word-vectors"
    rsync -avzr vacc1:/users/c/d/cdanfort/scratch/twitter/daily-wordcounts-${LANG}/parsed.${DAY}.csv word-vectors/${LANG}
    # rsync -avzr vacc2:/users/c/d/cdanfort/scratch/twitter/daily-wordcounts/parsed.${DAY}.csv word-vectors

    # get rid of the file
    # rm word-vectors/parsed.$(date +%Y-%m-%d).csv 

    if [ -f word-vectors/${LANG}/parsed.${DAY}.csv ]; then
	echo "python transform10k.py parsed.${DAY}.csv"
	python transform10kPolyGlot.py ${DAY} ${LANG}

	echo "python rest.py prevvectors ${DAY} ${DAY} ${LANG}"
	python rest.py prevvectors ${DAY} ${DAY} ${LANG}

	echo "python timeseries.py ${DAY} ${DAY} append ${LANG}"
	python timeseries.py ${DAY} ${DAY} append ${LANG}

	echo "python preshift.py prevvectors ${DAY} ${DAY} ${LANG}"
	python preshift.py ${DAY} ${DAY} ${LANG}

	. /home/prod/.env
	echo "python addtomodel.py $(tail -n 1 word-vectors/sumhapps.csv) ${LANG}"
	python addtomodel.py $(tail -n 1 word-vectors/sumhapps.csv) ${LANG}

	# /usr/local/share/phantomjs /root/phantom-crowbar/phantom-crowbar.js http://hedonometer.org/index.html?date=$(date +%Y-%m-%d -d "29 hours ago") shiftsvg /usr/share/nginx/data/screenshots/$(date +%Y-%m-%d -d "5 hours ago")/index-shift.svg
	# /usr/bin/convert /usr/share/nginx/data/screenshots/$(date +%Y-%m-%d -d "5 hours ago")/index-shift.svg /usr/share/nginx/data/screenshots/$(date +%Y-%m-%d -d "5 hours ago")/index-shift.png
	# echo "python hedotweet.py ${DAY}"
        # python hedotweet.py ${DAY}

    fi
else
    echo "word-vectors/${LANG}/parsed.${DAY}.csv found"
fi

# fixed the python script to save there
# mv word-vectors/${DAY}-{meta,}shift.csv shifts

# rm allhappsday.csv 
# echo "date,value" >> allhappsday.csv 
# for f in word-vectors/*sumhapps.csv; do (cat "${f}"; echo) >> allhappsday.csv; done



