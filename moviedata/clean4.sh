for FILE in $(\ls -1 rawer/*.html)
do 
    cat $FILE.end.beg | sed -e "s/<[^>]\{2,\}>//gi" > $FILE.clean04
done

