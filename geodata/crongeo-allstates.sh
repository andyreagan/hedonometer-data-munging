# pick an offset
OFFSET=1

# or do a lot
for OFFSET in {243..1} # 1 # {50..1}
do

DAY=$(date +%Y-%m-%d -d "${OFFSET} days ago")
echo ${DAY}
for STATE in {1..51} all
do 
  # \rm word-vectors/${STATE}/${DAY}-${STATE}-word-vector.csv
  rsync -avzr vacc1:/users/a/r/areagan/fun/twitter/jake/pullTweets/word-vectors/${DAY}-${STATE}-word-vector.csv word-vectors/${STATE}
  python rest.py previous ${DAY} 7 word-vectors/${STATE}/${DAY}-${STATE}-word-vector-previous7.csv ${STATE}
  python rest.py previous ${DAY} 30 word-vectors/${STATE}/${DAY}-${STATE}-word-vector-previous30.csv ${STATE}
  python rest.py previous ${DAY} 90 word-vectors/${STATE}/${DAY}-${STATE}-word-vector-previous90.csv ${STATE}
done

# finish the many offsets
done