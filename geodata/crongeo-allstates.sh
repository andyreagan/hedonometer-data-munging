
DAY=2014-11-30
for STATE in {1..51} all
do 
  rsync -avzr vacc1:/users/a/r/areagan/fun/twitter/jake/pullTweets/${DAY}-${STATE}-word-vector.csv word-vectors/${STATE}
  python rest.py previous ${DAY} 7 word-vectors/${STATE}/${DAY}-${STATE}-word-vector-previous7.csv ${STATE}
  python rest.py previous ${DAY} 30 word-vectors/${STATE}/${DAY}-${STATE}-word-vector-previous30.csv ${STATE}
  python rest.py previous ${DAY} 90 word-vectors/${STATE}/${DAY}-${STATE}-word-vector-previous30.csv ${STATE}
done