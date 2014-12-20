echo "stage 1"
cd rawer/trouble
for FILE in $(\ls -1 *.html)
do 
    # mv $FILE{,.lewis}
    # wget http://www.imsdb.com/scripts/$FILE
    # mv $FILE rawer/redownload
    # sed -i "s/<tt>//" $FILE
    # sed -i "s/<\/tt>//" $FILE
    # sed -i "s/<font size=\"-1\">//" $FILE
    # sed -i "s/<\/font>//" $FILE
    grep -A 1000000 "class=scrtext" $FILE | sed -n '2,1000000p' > $FILE.end
done
echo "stage 2"
# for FILE in $(\ls -1 rawer/*.html.end)
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
