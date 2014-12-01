for FILE in $(\ls -1 word-vectors)
do
    echo "python maketimeseries.py ${FILE}"
    python maketimeseries.py ${FILE}
done
