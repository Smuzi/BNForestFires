import numpy as np
import time
from cpt_maker import create_cpt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas


# query: P(area|temp=t,RH=h)
# node_list: [node1,node2..], parents_list [[node1_parent1,node1_parent2..],[..],..]
# if a node has not parents, empty list [].
# variable elimination order: day,month,rain,wind,ffmc,dmc,dc,isi (nodes x,y are isolated)
def variable_elimination(node_list, parents_list,node_vals,RH_set=0,temp_set=0):
    start_time = time.clock()
    # nodes = ['X', 'Y', 'month', 'day', 'FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain', 'area']
    # elimination_order = ['day', 'month', 'rain', 'wind', 'FFMC', 'DMC', 'DC', 'ISI']
    # print 'node elimination order:' + str(elimination_order)

    # sum over day: p(day)*p(RH=h|day)*p(wind|month,day)
    p_day = create_cpt('day',node_vals['day'],[],[])                            # 7x1 (1x1 for specific day)
    p_RH_given_day = create_cpt('RH',node_vals['RH'],['day'],[7])               # 5x7 - unnecessary
    evidence_RH_given_day = p_RH_given_day[RH_set, :]                           # 1x7 / 7x1 (1x1 for specific day)
    p_wind_given_month_day = create_cpt('wind',node_vals['wind'],['month','day'],
                                        [node_vals['month'],node_vals['day']])  # 5x12x7 (5x12 for specific day)
    sum_var_1 = np.zeros(p_wind_given_month_day[:, :, 0].shape)                 # 5x12: wind x month
    for val in range(node_vals['day']):
        sum_var_1 += p_day[val] * evidence_RH_given_day[val] * p_wind_given_month_day[:, :, val]

    # sum over month: p(month)*p(temp=t|month)*p(rain|month)
    p_month = create_cpt('month',node_vals['month'],[],[])                                      # 12x1
    p_temp_given_month = create_cpt('temp',node_vals['temp'],['month'],[node_vals['month']])    # 5x12 - unnecessary
    evidence_temp_given_month = p_temp_given_month[temp_set, :]                                 # 12x1/1x12
    p_rain_given_month = create_cpt('rain',node_vals['rain'],['month'],[node_vals['month']])    # 5x12

    sum_var_2 = np.zeros((np.matrix(sum_var_1[:, 0]).transpose()*p_rain_given_month[:, 0]).shape)  # 5x5 : wind x rain
    for val in range(node_vals['month']):
        sum_var_2 += np.matrix(sum_var_1[:, val]).transpose() * p_month[val] * evidence_temp_given_month[val] * \
                     p_rain_given_month[:, val]


    # sum over rain: p(FFMC|temp=t,RH=h,rain,wind)*p(DMC|temp=t,RH=h,rain)*p(DC|temp=t,rain)
    p_FFMC_given_4 = create_cpt('FFMC',node_vals['FFMC'],['temp','RH','rain','wind'],
                                [node_vals[p] for p in ['temp','RH','rain','wind']])    # 5x5x5x5x5 unused
    evidence_FFMC = p_FFMC_given_4[:, temp_set, RH_set, :, :]                           # 5x5x5: ffmc x rain x wind
    p_DMC_given_3 = create_cpt('DMC',node_vals['DMC'],['temp','RH','rain'],
                               [node_vals[p] for p in ['temp','RH','rain']])            # 5x5x5x5 unused
    evidence_DMC = p_DMC_given_3[:, temp_set, RH_set, :]                                # 5x5: dmc x rain
    p_DC_given_2 = create_cpt('DC',node_vals['DC'],['temp','rain'],
                              [node_vals[p] for p in ['temp','rain']])                  # 5x5x5 unused
    evidence_DC = p_DC_given_2[:, temp_set, :]                                          # 5x5: dc x rain

    sum_var_3 = np.zeros((node_vals['FFMC'], node_vals['wind'], node_vals['DMC'],
                          node_vals['DC']))                                             # FFMc x wind x DMC x DC

    # print sum_var_3.shape                                                             # 5 x 5 x 5 x 5
    for val in range(node_vals['rain']):
        temp_var = np.zeros((node_vals['FFMC'], node_vals['wind']))                     # FFMC x wind
        temp_ffmc = evidence_FFMC[:, val, :]
        for w_val in range(node_vals['wind']):
            temp_var[:, w_val] = temp_ffmc[:,w_val] * sum_var_2[w_val, val]
        # for w_val in range(node_vals['wind']):
        #     temp_var[:, w_val] = evidence_FFMC[:, val, w_val] * sum_var_2[w_val, val]
        temp_var = temp_var[:, :, np.newaxis]                                           # FFMC x wind x DMC (5x5x1)
        temp_var_2 = temp_var * evidence_DMC[:, val]                                    # 5 x 5 x 5
        temp_var_2 = temp_var_2[:, :, :, np.newaxis]                                    # FFMC x wind x DMC xDC(5x5x5x1)
        sum_var_3 += temp_var_2 * evidence_DC[:, val]

    # sum over wind: p(ISI|FFMC,wind)
    p_ISI_given_2 = create_cpt('ISI', node_vals['ISI'], ['FFMC', 'wind'], [node_vals['FFMC'],
                                                                           node_vals['wind']])  # 5x5x5
    sum_var_4 = np.zeros((node_vals['FFMC'], node_vals['DMC'], node_vals['DC'],
                          node_vals['ISI']))                                            # FFMC x DMC x DC x ISI
    for val in range(node_vals['wind']):
        temp_ISI = p_ISI_given_2[:, :, val]                                             # ISI X FFMC
        temp_sum_var_3 = sum_var_3[:, val, :, :]                                        # FFMC x DMC x DC
        for f_val in range(node_vals['FFMC']):
            sum_var_4[f_val, :, :, :] += temp_sum_var_3[f_val, :, :, np.newaxis] * \
                                        p_ISI_given_2[:, f_val]                         # 5x5x1 X 1x5 = 5x5x5

    # sum over ffmc - no more cpt to account for except the leftovers from previous variables:
    sum_var_5 = np.sum(sum_var_4, axis=0)                                                # DMC x DC x ISI

    # sum over DMC - p(area|DMC,DC,ISI)
    p_area_given_3 = create_cpt('area', node_vals['area'], ['DMC', 'DC','ISI'],
                                [node_vals['DMC'], node_vals['DC'], node_vals['ISI']])  # area x DMC x DC x ISI : 5x5x5

    sum_var_6 = np.zeros((node_vals['area'], node_vals['DC'], node_vals['ISI']))        # area x DC x ISI
    for val in range(node_vals['DMC']):
        temp_sum_var = sum_var_5[val, :, :]                                             # DC x ISI
        temp_area = p_area_given_3[:, val, :, :]                                        # area x DC x ISI
        for val_dc in range(node_vals['DC']):
            for val_isi in range(node_vals['ISI']):
                sum_var_6[:, val_dc, val_isi] += temp_area[:, val_dc, val_isi] * temp_sum_var[val_dc, val_isi]

    # sum over dc:
    sum_var_7 = np.sum(sum_var_6, axis=1)

    # sum over isi:
    area_probability = np.sum(sum_var_7, axis=1)

    # normalization:
    if sum(area_probability) == 0:
        area_probability = np.zeros(area_probability.shape)
    else:
        area_probability = area_probability / sum(area_probability)

    # print 'time taken: ' + str(time.clock()-start_time)
    return area_probability


def plot_results(fire_size_var=0,dump=False):
    results_list = []
    path = 'variable_elimination_results.txt'
    # path = 'forward_sampling_results.txt'
    with open(path, 'r') as f:
        split_rows = map(lambda line: line.split(' '), f.readlines())
        for line in split_rows:
            current_res = {}
            current_res[0] = line[3]
            current_res[1] = line[4]
            current_res[2] = line[5]
            current_res[3] = line[6]
            current_res[4] = line[7]
            results_list.append(current_res)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    xpos_rh = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4]
    ypos_temp = [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4]
    zpos = np.zeros_like(xpos_rh)
    dx = dy = [0.5 for i in range(25)]
    dz = []
    for i in range(5):
        for j in range(5):
            current_index = i*5+j
            prob = (results_list[current_index])[fire_size_var]
            # print prob
            dz.append(float(prob))
            # dz.append(current_index)

    ax.bar3d(xpos_rh, ypos_temp, zpos, dx, dy, dz, color=['b', 'g', 'y', 'r', 'c']*5, zsort='average')
    plt.xlabel('humidity indicator')
    plt.ylabel('temperature indicator')
    if dump:
        plt.savefig('VE_res_'+str(fire_size_var)+'.png')
    plt.show()

def generate_graphs(dump=False):
    for i in range(5):
        plot_results(i, dump)

if __name__ == '__main__':
    all_nodes = ['X', 'Y', 'month', 'day', 'FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain', 'area']
    all_parents = [[], [], [], [], ['temp', 'RH', 'wind', 'rain'], ['temp', 'RH', 'rain'], ['temp', 'rain'],
               ['FFMC', 'wind'], ['month'], ['day'], ['month', 'day'], ['month'], ['DMC', 'DC', 'ISI']]

    node_value_count = {'X':10, 'Y':10, 'month':12, 'day':7, 'FFMC':5, 'DMC':5, 'DC':5, 'ISI':5, 'temp':5, 'RH':5, 'wind':5, 'rain':5, 'area':5}
    start_time = time.clock()
    # print "Variable elimination process:"
    # elimination_order = ['day', 'month', 'rain', 'wind', 'FFMC', 'DMC', 'DC', 'ISI']
    # print 'node elimination order:' + str(elimination_order)
    # for i in range(5):
    #     for j in range(5):
    #         results = variable_elimination(all_nodes, all_parents, node_value_count,RH_set=i,temp_set=j)
    #         print "RH=" + str(i) + " temp=" + str(j) + " burned_area:" + str(results)

    # generate_graphs(dump=False)
    print 'total time: ' + str(time.clock()-start_time)

