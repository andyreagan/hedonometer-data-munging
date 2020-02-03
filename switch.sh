for d in word-vectors shifts; do
  cd $d
  rm vacc
  ln -s vacc{-josh,}
  # ln -s vacc{-andy,}
  cd ..
done
