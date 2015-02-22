HTMLFOLDER="rawer-take2"

wget http://www.theraffon.net/~spookcentral/gb1_script_1983-10-07.htm

chmod 644 ${HTMLFOLDER}/*.html
\rm ${HTMLFOLDER}/*.end
\rm ${HTMLFOLDER}/*.end.beg
\rm ${HTMLFOLDER}/*.end.beg.clean
\rm ${HTMLFOLDER}/*.clean*
\rm ${HTMLFOLDER}/trouble/*

echo "stage 1"
for FILE in $(\ls -1 ${HTMLFOLDER}/*.html)
do 
    sed -i "s/<tt>//" $FILE
    grep -A 1000000 "class=\"scrtext\"" $FILE | sed -n '2,1000000p' > $FILE.end
done
echo "stage 2"
# for FILE in $(\ls -1 ${HTMLFOLDER}/*.html.end)
# do
#     grep -B 1000000 "</body>" $FILE > $FILE.beg
# done
for FILE in $(\ls -1 ${HTMLFOLDER}/*.html.end)
do
    grep -B 1000000 -m 1 "</pre>" $FILE > $FILE.beg
done
echo "stage 3"
for FILE in $(\ls -1 ${HTMLFOLDER}/*.html.end.beg)
do
    sed -i '$ d' $FILE
done
echo "stage 4"
for FILE in $(\ls -1 ${HTMLFOLDER}/*.html.end.beg)
do
    cat $FILE | sed -e "s/<b>//" | sed -e "s/<\/b>//" > $FILE.clean
done

########################################
# this checks that there is something left 

mkdir ${HTMLFOLDER}/trouble
mkdir ${HTMLFOLDER}/trouble/redownload

for FILE in $(\ls -1 ${HTMLFOLDER}/*.html)
do 
    SIZE=$(du -b $FILE.end.beg | cut -f1)
    if [ $((SIZE)) -le 4000 ]
    then
	echo "failed first parse on $FILE"
	# \rm $FILE.*
	cp $FILE ${HTMLFOLDER}/trouble
    fi
done

########################################
# this goes for the ones that didn't work well with the above

echo "stage 1"
cd ${HTMLFOLDER}/trouble
for FILE in $(\ls -1 *.html)
do 
    mv $FILE{,.lewis}
    wget http://www.imsdb.com/scripts/$FILE
    mv $FILE ${HTMLFOLDER}/redownload
    # sed -i "s/<tt>//" $FILE
    # sed -i "s/<\/tt>//" $FILE
    # sed -i "s/<font size=\"-1\">//" $FILE
    # sed -i "s/<\/font>//" $FILE
    grep -A 1000000 "class=scrtext" $FILE | sed -n '2,1000000p' > $FILE.end
done

echo "stage 2"
# for FILE in $(\ls -1 ${HTMLFOLDER}/*.html.end)
# do
#     grep -B 1000000 "</body>" $FILE > $FILE.beg
# done
for FILE in $(\ls -1 *.html.end)
do
    grep -B 1000000 -m 1 "</body>" $FILE > $FILE.beg
done

echo "stage 3"
for FILE in $(\ls -1 *.html.end.beg)
do
    sed -i '$ d' $FILE
done
echo "stage 4"
for FILE in $(\ls -1 *.html.end.beg)
do
    cat $FILE | sed -e "s/<b>//" | sed -e "s/<\/b>//" > $FILE.clean
done
cd ../../

########################################
# take a different approach

for FILE in $(\ls -1 ${HTMLFOLDER}/*.html)
do 
    cat $FILE.end.beg | sed -e "s/<[:\. -=?%#;\"'a-zA-Z0-9\n\\/]\{3,\}>//gi" > $FILE.clean01
    cat $FILE.end.beg | sed -e "s/<[^>]\{3,\}>//gi" > $FILE.clean02
    # cat $FILE.end.beg | sed -e "s/<[.]\{3,\}>//gi" > $FILE.clean03
    # cat $FILE.end.beg | sed -e "s/<[^b]{1}>//gi" > $FILE.clean02
done

for FILE in $(\ls -1 ${HTMLFOLDER}/*.html)
do 
    cat $FILE.end.beg | sed -e "s/<[^>]\{2,\}>//gi" > $FILE.clean04
done



