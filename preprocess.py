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
            # plt.hist(column)
            # plt.ylabel(str(name)+' distribution')
            # plt.show()
        print '---'
    # plt.plot(x_list)
    # plt.ylabel('bb')
    # plt.show()
    return df
#DMC ISI rain area are badly distributed

def turn_month_to_num(month_col):
    tmp_list = []
    for val in month_col:
        if val == 'jan':
            tmp_list.append(0)
        elif val == 'feb':
            tmp_list.append(1)
        elif val == 'mar':
            tmp_list.append(2)
        elif val == 'apr':
            tmp_list.append(3)
        elif val == 'may':
            tmp_list.append(4)
        elif val == 'jun':
            tmp_list.append(5)
        elif val == 'jul':
            tmp_list.append(6)
        elif val == 'aug':
            tmp_list.append(7)
        elif val == 'sep':
            tmp_list.append(8)
        elif val == 'oct':
            tmp_list.append(9)
        elif val == 'nov':
            tmp_list.append(10)
        elif val == 'dec':
            tmp_list.append(11)
    return tmp_list



def turn_day_to_num(day_col):
    tmp_list = []
    for val in day_col:
        if val == 'sun':
            tmp_list.append(0)
        elif val == 'mon':
            tmp_list.append(1)
        elif val == 'tue':
            tmp_list.append(2)
        elif val == 'wed':
            tmp_list.append(3)
        elif val == 'thu':
            tmp_list.append(4)
        elif val == 'fri':
            tmp_list.append(5)
        elif val == 'sat':
            tmp_list.append(6)
    return tmp_list


split_size = 5
def data_to_discrete(data_table, dump=False):
    print 'turning data to discrete values - each range of values is divided to '+ str(split_size) + ' ranges from 0-'+str(split_size-1)
    col_names = data_table.columns
    for col in col_names:
        if col == 'FFMC'.encode('utf-8') or col == 'ISI'.encode('utf-8'):               # mean-(3/2)sigma,mean-sigma/2, mean, mean + sigma/2, rest
            ffmc_col = data_table[col]
            sigma = np.sqrt(np.var(ffmc_col))
            mean = np.mean(ffmc_col)
            for i,val in enumerate(ffmc_col):
                real_val = 0
                if val > mean:
                    if val > (mean+sigma/2):
                        real_val = 4
                    else:
                        real_val = 3
                else:
                    if val < (mean-sigma/2):
                        if val < (mean-3*sigma/2):
                            real_val = 0
                        else:
                            real_val = 1
                    else:
                        real_val = 2
                data_table.set_value(i, col, real_val)
        elif col == 'area'.encode('utf-8') or col == 'rain'.encode('utf-8'):
            area_col = data_table[col]
            sigma = np.sqrt(np.var([i for i in area_col if i > 0]))
            mean = np.mean([i for i in area_col if i > 0])
            for i,val in enumerate(area_col):
                real_val = 0
                if val > 0:
                    if val > mean:
                        if val > (2*mean):
                            real_val = 4
                        else:
                            real_val = 3
                    elif val < (mean/2):
                        real_val = 1
                    else:
                        real_val = 2
                data_table.set_value(i, col, real_val)
        # elif col == 'ISI'.encode('utf-8'):
        #     isi_col = data_table[col]
        #     sigma = np.sqrt(np.var(isi_col))
        #     mean = np.mean(isi_col)
        #     print sigma,mean
        #     exit()
        #     # for i, val in enumerate(ffmc_col):
        # elif col == 'rain'.encode('utf-8'):
        #     rain_col = data_table[col]
        #     sigma = np.sqrt(np.var(rain_col))
        #     mean = np.mean(rain_col)
        #     print mean, sigma
        #
        #     sigma = np.sqrt(np.var([i for i in rain_col if i > 0]))
        #     mean = np.mean([i for i in rain_col if i > 0])
        #     print mean, sigma
        #     exit()
        #     for i,val in enumerate(rain_col):
        #         real_val = 0
        #         # if val > 0:
        #     exit()
        elif col == 'month'.encode('utf-8'):
            month_col = data_table[col]
            month_num_col = turn_month_to_num(month_col)
            for i, val in enumerate(month_num_col):
                data_table.set_value(i, col, val)
        elif col == 'day'.encode('utf-8'):
            day_col = data_table[col]
            day_num_col = turn_day_to_num(day_col)
            for i, val in enumerate(day_num_col):
                data_table.set_value(i, col, val)
        elif (col != 'X'.encode('utf-8')) & (col != 'Y'.encode('utf-8')):
            data_column = data_table[col]
            col_min = min(data_column)
            range = max(data_column) - col_min
            delta = range/split_size
            #print 'reformatting: '+ str(col)
            #print data_column
            for i,val in enumerate(data_column.values):
                bucket = (val-col_min) // delta            ##needs to be checked
                #  print 'i:' + str(i) +' '+ str(bucket) +' '+ str (val)
                if int(bucket) == 5:
                    bucket = 4
                data_table.set_value(i, col, int(bucket))
                # copy_col[i] = int(bucket)
            # data_table[col] = copy_col
    if dump:
        print 'writing new table to forest_fires_correct_2.csv'
        data_table.to_csv('forest_fires_correct_2.csv', sep=',', index=False, encoding='utf-8')
    return data_table


if __name__ == '__main__':
    data_path = "./forestfires.csv"
    latest_path = "./forest_fires_correct_2.csv"
    # data_table = get_column_stats(latest_path)
    # exit()
    data_table = get_column_stats(data_path)
    # print data_table
    data_table = data_to_discrete(data_table, dump=False)
    # print data_table

