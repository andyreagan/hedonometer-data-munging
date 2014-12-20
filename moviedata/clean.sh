echo "stage 1"
for FILE in $(\ls -1 rawer/*.html)
do 
    sed -i "s/<tt>//" $FILE
    grep -A 1000000 "class=\"scrtext\"" $FILE | sed -n '2,1000000p' > $FILE.end
done
echo "stage 2"
# for FILE in $(\ls -1 rawer/*.html.end)
# do
#     grep -B 1000000 "</body>" $FILE > $FILE.beg
# done
for FILE in $(\ls -1 rawer/*.html.end)
do
    grep -B 1000000 -m 1 "</pre>" $FILE > $FILE.beg
done
echo "stage 3"
for FILE in $(\ls -1 rawer/*.html.end.beg)
do
    sed -i '$ d' $FILE
done
echo "stage 4"
for FILE in $(\ls -1 rawer/*.html.end.beg)
do
    cat $FILE | sed -e "s/<b>//" | sed -e "s/<\/b>//" > $FILE.clean
done
