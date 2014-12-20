for FILE in $(\ls -1 rawer/*.html)
do 
    SIZE=$(du -b $FILE.end.beg | cut -f1)
    if [ $((SIZE)) -le 4000 ]
    then
	echo $FILE
	# \rm $FILE.*
	mv $FILE rawer/trouble
    fi
done