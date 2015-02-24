HTMLFOLDER="rawer-take2/redownload"

chmod 644 ${HTMLFOLDER}/*.html
\rm ${HTMLFOLDER}/*.end*
\rm ${HTMLFOLDER}/*.clean*

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
done

########################################
# this checks that there is something left 

for FILE in $(\ls -1 ${HTMLFOLDER}/*.html)
do 
    SIZE=$(du -b $FILE.end.beg | cut -f1)
    if [ $((SIZE)) -le 4000 ]
    then
	echo "still failed first parse on $FILE"
	sed -i "s/<tt>//" $FILE
	# sed -i "s/\"scrtext\"/scrtext/" $FILE
	grep -A 1000000 "class=\"scrtext\"" $FILE | sed -n '2,1000000p' > $FILE.end
	# cat $FILE.end > $FILE.end.beg
	grep -B 1000000 -m 1 "</table>" $FILE.end > $FILE.end.beg
	sed -i '$ d' $FILE.end.beg
	cat $FILE.end.beg | sed -e "s/<b>//" | sed -e "s/<\/b>//" > $FILE.end.beg.clean
    fi
    cat $FILE.end.beg | sed -e "s/<[:\. -=?%#;\"'a-zA-Z0-9\n\\/]\{3,\}>//gi" > $FILE.clean01
    cat $FILE.end.beg | sed -e "s/<[^>]\{3,\}>//gi" > $FILE.clean02
    cat $FILE.end.beg | sed -e "s/<[.]\{3,\}>//gi" > $FILE.clean03
    cat $FILE.end.beg | sed -e "s/<[^>]\{2,\}>//gi" > $FILE.clean04
    cat $FILE.end.beg | sed -e "s/<[^b]{1}>//gi" > $FILE.clean05
    SIZE=$(du -b $FILE.end.beg | cut -f1)
    if [ $((SIZE)) -le 4000 ]
    then
	echo "still still failed first parse on $FILE"
    else
	cp $FILE $FILE.end $FILE.end.beg $FILE.end.beg.clean rawer-take2
	cp $FILE.clean0{1..5} rawer-take2
    fi
done






