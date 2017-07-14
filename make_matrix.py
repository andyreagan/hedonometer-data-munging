from scipy.sparse import csr_matrix,lil_matrix,coo_matrix
# coo does not support slicing, but better for building in general
# lil is row-based, so I'll add to rows
from datetime import datetime,timedelta,date
from numpy import genfromtxt,savetxt
from os.path import isfile
import lz4
import pickle

start_date = date(2008,9,13)
end_date = date(2015,11,23)
end_date = date.today()+timedelta(days=1)

delta = end_date - start_date
n_days = delta.days
full_matrix = lil_matrix((n_days,10222),dtype="i")
print(full_matrix.shape)
curr_date = start_date
i = 0
while curr_date <= end_date:
    fname = curr_date.strftime("word-vectors/vacc/%Y-%m-%d-sum.csv")
    if isfile(fname):
        print("loading",fname)
        print(full_matrix.shape)
        today_vec = genfromtxt(fname,
                               dtype="i")
        print(today_vec[:10])
        full_matrix[i,:] = today_vec
    else:
        print("missing",fname)
    i+=1
    curr_date+=timedelta(days=1)

# f = open("all_wordvecs_matrix.p","wb")
# f.write(lz4.compress(pickle.dumps(full_matrix,pickle.HIGHEST_PROTOCOL)))
# f.close()

savetxt("all_wordvecs_matrix.csv.gz",full_matrix.todense(),fmt="%.0f",delimiter=",")
