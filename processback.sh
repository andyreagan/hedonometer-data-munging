# go back and do the stuff for arabic# this job runs from cron every hour

LANG=arabic

. /home/prod/.env

for BACK in {1000..1}
do
    DAY=$(date +%Y-%m-%d -d "$BACK days ago")
    echo "processing ${DAY} for ${LANG}"

    if [ -f word-vectors/${LANG}/parsed.${DAY}.csv ]; then
	echo "python transform10k.py parsed.${DAY}.csv"
	python transform10kPolyGlot.py ${DAY} ${LANG}

	echo "python rest.py prevvectors ${DAY} ${DAY} ${LANG}"
	python rest.py prevvectors ${DAY} ${DAY} ${LANG}

	echo "python preshift.py prevvectors ${DAY} ${DAY} ${LANG}"
	python preshift.py ${DAY} ${DAY} ${LANG}

	# echo "python timeseries.py ${DAY} ${DAY} append ${LANG}"
	# python timeseries.py ${DAY} ${DAY} append ${LANG}

	# don't add them to the model yet
	# echo "python addtomodel.py $(tail -n 1 word-vectors/sumhapps.csv) ${LANG}"
	# python addtomodel.py $(tail -n 1 word-vectors/sumhapps.csv) ${LANG}

	# /usr/local/share/phantomjs /root/phantom-crowbar/phantom-crowbar.js http://hedonometer.org/index.html?date=$(date +%Y-%m-%d -d "29 hours ago") shiftsvg /usr/share/nginx/data/screenshots/$(date +%Y-%m-%d -d "5 hours ago")/index-shift.svg
	# /usr/bin/convert /usr/share/nginx/data/screenshots/$(date +%Y-%m-%d -d "5 hours ago")/index-shift.svg /usr/share/nginx/data/screenshots/$(date +%Y-%m-%d -d "5 hours ago")/index-shift.png
	# echo "python hedotweet.py ${DAY}"
        # python hedotweet.py ${DAY}

    else
	echo "word-vectors/${LANG}/parsed.${DAY}.csv not found"
    fi
done

# fixed the python script to save there
# mv word-vectors/${DAY}-{meta,}shift.csv shifts

# rm allhappsday.csv 
# echo "date,value" >> allhappsday.csv 
# for f in word-vectors/*sumhapps.csv; do (cat "${f}"; echo) >> allhappsday.csv; done



