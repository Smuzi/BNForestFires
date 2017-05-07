import numpy as np
import time
from cpt_maker import create_cpt

# query: P(area|temp=t,RH=h)
# node_list: [node1,node2..], parents_list [[node1_parent1,node1_parent2..],[..],..]
# if a node has not parents, empty list [].
# variable elimination order: day,month,rain,wind,ffmc,dmc,dc,isi (nodes x,y are isolated)
def variable_elimination(node_list, parents_list,node_vals,RH_set=0,temp_set=0):
    start_time = time.clock()
    # nodes = ['X', 'Y', 'month', 'day', 'FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain', 'area']
    # node_cpt = {}
    # for (node, parents) in zip(node_list, parents_list):
    #     node_cpt[node] = create_cpt(node, node_vals[node], parents, [node_vals[p] for p in parents])
    elimination_order = ['day', 'month', 'rain', 'wind', 'FFMC', 'DMC', 'DC', 'ISI']
    # for i, var in enumerate(elimination_order):
    #     print str(i) + ' - summing over:' + str(var)
    #     if i == 0:  # day
    #         var_cpt = node_cpt[var]
    #         var_original_parents = parents_list[i + 2]  # add 2 to include x,y which are not summed
    #
    #         sum_var =

    # sum over day: p(day)*p(RH=h|day)*p(wind|month,day)
    print 'summing day.'
    p_day = create_cpt('day',node_vals['day'],[],[])                            # 7x1 (1x1 for specific day)
    p_RH_given_day = create_cpt('RH',node_vals['RH'],['day'],[7])               # 5x7 - unnecessary
    evidence_RH_given_day = p_RH_given_day[RH_set, :]                           # 1x7 / 7x1 (1x1 for specific day)
    p_wind_given_month_day = create_cpt('wind',node_vals['wind'],['month','day'],
                                        [node_vals['month'],node_vals['day']])  # 5x12x7 (5x12 for specific day)
    sum_var_1 = np.zeros(p_wind_given_month_day[:, :, 0].shape)                 # 5x12: wind x month
    for val in range(node_vals['day']):
        sum_var_1 += p_day[val] * evidence_RH_given_day[val] * p_wind_given_month_day[:, :, val]

    # sum over month: p(month)*p(temp=t|month)*p(rain|month)
    print 'summing month..'
    p_month = create_cpt('month',node_vals['month'],[],[])                                      # 12x1
    p_temp_given_month = create_cpt('temp',node_vals['temp'],['month'],[node_vals['month']])    # 5x12 - unnecessary
    evidence_temp_given_month = p_temp_given_month[temp_set, :]                                 # 12x1/1x12
    p_rain_given_month = create_cpt('rain',node_vals['rain'],['month'],[node_vals['month']])    # 5x12

    sum_var_2 = np.zeros((np.matrix(sum_var_1[:, 0]).transpose()*p_rain_given_month[:, 0]).shape)  # 5x5 : wind x rain
    for val in range(node_vals['month']):
        sum_var_2 += np.matrix(sum_var_1[:, val]).transpose() * p_month[val] * evidence_temp_given_month[val] * \
                     p_rain_given_month[:, val]


    # sum over rain: p(FFMC|temp=t,RH=h,rain,wind)*p(DMC|temp=t,RH=h,rain)*p(DC|temp=t,rain)
    print 'summing rain...'
    p_FFMC_given_4 = create_cpt('FFMC',node_vals['FFMC'],['temp','RH','rain','wind'],
                                [node_vals[p] for p in ['temp','RH','rain','wind']])    # 5x5x5x5x5 unused
    evidence_FFMC = p_FFMC_given_4[:, temp_set, RH_set, :, :]                           # 5x5x5: ffmc x rain x wind
    print evidence_FFMC
    print sum(sum(sum(evidence_FFMC)))
    exit()
    p_DMC_given_3 = create_cpt('DMC',node_vals['DMC'],['temp','RH','rain'],
                               [node_vals[p] for p in ['temp','RH','rain']])            # 5x5x5x5 unused
    evidence_DMC = p_DMC_given_3[:, temp_set, RH_set, :]                                # 5x5: dmc x rain
    p_DC_given_2 = create_cpt('DC',node_vals['DC'],['temp','rain'],
                              [node_vals[p] for p in ['temp','rain']])                  # 5x5x5 unused
    evidence_DC = p_DC_given_2[:, temp_set, :]                                          # 5x5: dc x rain

    sum_var_3 = np.zeros((node_vals['FFMC'], node_vals['wind'], node_vals['DMC'],
                          node_vals['DC']))                                             # FFMc x wind x DMC x DC

    # print sum_var_3.shape                                                             # 5 x 5 x 5 x 5
    # print sum_var_2[:, :, np.newaxis, np.newaxis, np.newaxis].shape
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
    print 'summing wind....'
    p_ISI_given_2 = create_cpt('ISI', node_vals['ISI'], ['FFMC', 'wind'], [node_vals['FFMC'],
                                                                           node_vals['wind']])  # 5x5x5
    sum_var_4 = np.zeros((node_vals['FFMC'], node_vals['DMC'], node_vals['DC'],
                          node_vals['ISI']))                                            # FFMC x DMC x DC x ISI
    # print sum_var_4.shape                                                               # 5 x 5 x 5 x 5
    for val in range(node_vals['wind']):
        temp_ISI = p_ISI_given_2[:, :, val]                                             # ISI X FFMC
        temp_sum_var_3 = sum_var_3[:, val, :, :]                                        # FFMC x DMC x DC
        for f_val in range(node_vals['FFMC']):
            sum_var_4[f_val, :, :, :] += temp_sum_var_3[f_val, :, :, np.newaxis] * \
                                        p_ISI_given_2[:, f_val]                         # 5x5x1 X 1x5 = 5x5x5

    # sum over ffmc - no more cpt to account for except the leftovers from previous variables:
    print 'summing ffmc.....'
    sum_var_5 = np.sum(sum_var_4, axis=0)                                                # DMC x DC x ISI
    # print sum_var_5.shape                                                               # 5 x 5 x 5

    # sum over DMC - p(area|DMC,DC,ISI)
    print 'summing dmc......'
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
    print 'summing dc.......'
    sum_var_7 = np.sum(sum_var_6, axis=1)

    # sum over isi:
    print 'summing isi.......'
    area_probability = np.sum(sum_var_7, axis=1)

    # normalization:
    area_probability = area_probability / sum(area_probability)
    print 'time taken: ' + str(time.clock()-start_time)
    return area_probability

if __name__ == '__main__':
    all_nodes = ['X', 'Y', 'month', 'day', 'FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain', 'area']
    all_parents = [[], [], [], [], ['temp', 'RH', 'wind', 'rain'], ['temp', 'RH', 'rain'], ['temp', 'rain'],
               ['FFMC', 'wind'], ['month'], ['day'], ['month', 'day'], ['month'], ['DMC', 'DC', 'ISI']]

    node_value_count = {'X':10, 'Y':10, 'month':12, 'day':7, 'FFMC':5, 'DMC':5, 'DC':5, 'ISI':5, 'temp':5, 'RH':5, 'wind':5, 'rain':5, 'area':5}

    print "Variable elimination process:"
    # for i in range(5):
    #     for j in range(5):
    #         results = variable_elimination(all_nodes, all_parents, node_value_count,RH_set=i,temp_set=j)
    #         print "RH=" + str(i) + " temp=" + str(j) + " burned_area:" + str(results)
    results = variable_elimination(all_nodes, all_parents, node_value_count, RH_set=4, temp_set=4)
    print "RH=" + str(4) + " temp=" + str(4) + " burned_area:" + str(results)
