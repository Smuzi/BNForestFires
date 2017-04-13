import time
import pandas
import numpy as np
from scipy import stats, integrate
import matplotlib.pyplot as plt
nodes = ['X','Y','month','day','FFMC','DMC','DC','ISI','temp','RH','wind','rain','area']

def get_column_stats(path):
    print 'parsing forestfires.csv:'
    start_time = time.clock()
    df = pandas.read_csv(path,encoding='utf-8')
    col_names = df.columns
    print 'number of samples: ' + str(len(df[col_names[0]]))
    for name in col_names:
        print name + ' column stats:'
        column = df[name]
        if isinstance(column[0], basestring):
            print set(column)
        else:
            print 'min: ' + str(min(column)) + ' max: ' + str(max(column)) + ' mean: ' + str(np.mean(column))
        print '---'
    # plt.plot(x_list)
    # plt.ylabel('bb')
    # plt.show()


if __name__ == '__main__':
    data_path = "./forestfires.csv"
    get_column_stats(data_path)

