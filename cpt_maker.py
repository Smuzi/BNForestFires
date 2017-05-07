import pandas
import numpy as np
from collections import Counter

# assuming binary node and 1 parent with 3 possible values 0,1,2
# p(node=0|parent=0) p(node=0|parent=1) p(node=0|parent=2)
# p(node=1|parent=0) p(node=1|parent=1) p(node=1|parent=2)

# assuming binary node and two binary parents:
# p(0|0,0) p(0|0,1) p(0|1,0) p(0|1,1)
# p(1|0,0) p(1|0,1) p(1|1,0) p(1|1,1)



def create_cpt(node_name,num_of_values, parents_name, parents_num_of_values):
    path = 'forest_fires_correct.csv'
    data_table = pandas.read_csv(path, encoding='utf-8')
    example_number = data_table.shape[0]
    # print example_number
    num_parents = len(parents_name)
    # parent_combinations = reduce(lambda x, y: x*y, parents_num_of_values)
    cpt = np.zeros(tuple([num_of_values]+parents_num_of_values))
    it = np.nditer(cpt, flags=['multi_index'])
    while not it.finished:
        indices_tuple = it.multi_index #indices tuple i.e. (0,1,2,5) p(0|1,2,5)
        if num_parents == 0:
            nominator = Counter(data_table[node_name] == indices_tuple[0])
            cpt[indices_tuple[0]] = nominator[True]/float(example_number)
        elif num_parents == 1:
            nominator = Counter((data_table[node_name] == indices_tuple[0]) & (data_table[parents_name[0]]==indices_tuple[1]))
            denominator = Counter((data_table[parents_name[0]] == indices_tuple[1]))
            if denominator[True] == 0:
                cpt[indices_tuple[0]][indices_tuple[1]] = 0
            else:
                cpt[indices_tuple[0]][indices_tuple[1]] = nominator[True]/float(denominator[True])
        elif num_parents == 2:
            nominator = Counter((data_table[node_name] == indices_tuple[0]) & (data_table[parents_name[0]] == indices_tuple[1]) & (data_table[parents_name[1]] == indices_tuple[2]))
            denominator = Counter((data_table[parents_name[0]] == indices_tuple[1]) & (data_table[parents_name[1]] == indices_tuple[2]))
            if denominator[True] == 0:
                cpt[indices_tuple[0]][indices_tuple[1]][indices_tuple[2]] = 0
            else:
                cpt[indices_tuple[0]][indices_tuple[1]][indices_tuple[2]] = nominator[True] / float(denominator[True])
        elif num_parents == 3:
            nominator = Counter((data_table[node_name] == indices_tuple[0]) & (data_table[parents_name[0]] == indices_tuple[1]) & (data_table[parents_name[1]] == indices_tuple[2]) & (data_table[parents_name[2]] == indices_tuple[3]))
            denominator = Counter((data_table[parents_name[0]] == indices_tuple[1]) & (data_table[parents_name[1]] == indices_tuple[2]) & (data_table[parents_name[2]] == indices_tuple[3]))
            if denominator[True] == 0:
                cpt[indices_tuple[0]][indices_tuple[1]][indices_tuple[2]][indices_tuple[3]] = 0
            else:
                cpt[indices_tuple[0]][indices_tuple[1]][indices_tuple[2]][indices_tuple[3]] = nominator[True] / float(denominator[True])
        elif num_parents == 4:
            nominator = Counter((data_table[node_name] == indices_tuple[0]) & (data_table[parents_name[0]] == indices_tuple[1]) & (data_table[parents_name[1]] == indices_tuple[2]) & (data_table[parents_name[2]] == indices_tuple[3]) & (data_table[parents_name[3]] == indices_tuple[4]))
            denominator = Counter((data_table[parents_name[0]] == indices_tuple[1]) & (data_table[parents_name[1]] == indices_tuple[2]) & (data_table[parents_name[2]] == indices_tuple[3]) & (data_table[parents_name[3]] == indices_tuple[4]))
            if denominator[True] == 0:
                # cpt[indices_tuple[0]][indices_tuple[1]][indices_tuple[2]][indices_tuple[3]][indices_tuple[4]] = 0
                cpt[indices_tuple[0], indices_tuple[1], indices_tuple[2], indices_tuple[3], indices_tuple[4]] = 0
            else:
                # cpt[indices_tuple[0]][indices_tuple[1]][indices_tuple[2]][indices_tuple[3]][indices_tuple[4]] = nominator[True] / float(denominator[True])
                cpt[indices_tuple[0], indices_tuple[1], indices_tuple[2], indices_tuple[3], indices_tuple[4]] = nominator[True] / float(denominator[True])
        it.iternext()
    return cpt

if __name__ == '__main__':

    create_cpt('RH', 5, ['day'], [7])  # needs further checking with more than 1 parent
