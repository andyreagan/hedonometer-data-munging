HTMLFOLDER="rawer-take2"

# wget http://www.theraffon.net/~spookcentral/gb1_script_1983-10-07.htm
# \rm ${HTMLFOLDER}/Ghostbusters.html
# cp gb1_script_1983-10-07.htm ${HTMLFOLDER}/Ghostbusters.html

chmod 644 ${HTMLFOLDER}/*.html
\rm ${HTMLFOLDER}/*.end*
\rm ${HTMLFOLDER}/*.clean*
# \rm ${HTMLFOLDER}/trouble/*
# \rm ${HTMLFOLDER}/trouble/*.end*
# \rm ${HTMLFOLDER}/trouble/*.clean*

echo "stage 1"
for FILE in $(\ls -1 ${HTMLFOLDER}/*.html)
do 
    echo ${FILE}
    sed -i "s/<tt>//" $FILE
    # sed -i "s/\"scrtext\"/scrtext/" $FILE
    grep -A 1000000 "class=\"scrtext\"" $FILE | sed -n '2,1000000p' > $FILE.end
    grep -B 1000000 -m 1 "</pre>" $FILE.end > $FILE.end.beg
    sed -i '$ d' $FILE.end.beg
    cat $FILE.end.beg | sed -e "s/<b>//" | sed -e "s/<\/b>//" > $FILE.end.beg.clean
    cat $FILE.end.beg | sed -e "s/<[:\. -=?%#;\"'a-zA-Z0-9\n\\/]\{3,\}>//gi" > $FILE.clean01
    cat $FILE.end.beg | sed -e "s/<[^>]\{3,\}>//gi" > $FILE.clean02
    cat $FILE.end.beg | sed -e "s/<[.]\{3,\}>//gi" > $FILE.clean03
    cat $FILE.end.beg | sed -e "s/<[^>]\{2,\}>//gi" > $FILE.clean04
    cat $FILE.end.beg | sed -e "s/<[^b]{1}>//gi" > $FILE.clean05
done

########################################
# this checks that there is something left 

# mkdir ${HTMLFOLDER}/trouble
# mkdir ${HTMLFOLDER}/trouble/redownload

for FILE in $(\ls -1 ${HTMLFOLDER}/*.html)
do 
    SIZE=$(du -b $FILE.end.beg | cut -f1)
    if [ $((SIZE)) -le 4000 ]
    then
	echo "still failed first parse on $FILE"
	# \rm $FILE.*
	# cp $FILE ${HTMLFOLDER}/trouble
    fi
done

