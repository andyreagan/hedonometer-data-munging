for FILE in $(\ls -1 rawer/*.html)
do 
    cat $FILE.end.beg | sed -e "s/<[:\. -=?%#;\"'a-zA-Z0-9\n\\/]\{3,\}>//gi" > $FILE.clean01
    cat $FILE.end.beg | sed -e "s/<[^>]\{3,\}>//gi" > $FILE.clean02
    # cat $FILE.end.beg | sed -e "s/<[.]\{3,\}>//gi" > $FILE.clean03
    # cat $FILE.end.beg | sed -e "s/<[^b]{1}>//gi" > $FILE.clean02
done

