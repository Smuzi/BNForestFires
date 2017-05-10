import time
from cpt_maker import *


def forward_sampling(RH_set=0,temp_set=0):
    nodes = ['X', 'Y', 'month', 'day', 'FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain', 'area']
    all_parents = [[], [], [], [], ['temp', 'RH', 'wind', 'rain'], ['temp', 'RH', 'rain'], ['temp', 'rain'],
                   ['FFMC', 'wind'], ['month'], ['day'], ['month', 'day'], ['month'], ['DMC', 'DC', 'ISI']]
    node_vals = {'X': 10, 'Y': 10, 'month': 12, 'day': 7, 'FFMC': 5, 'DMC': 5, 'DC': 5, 'ISI': 5, 'temp': 5,
                 'RH': 5, 'wind': 5, 'rain': 5, 'area': 5}

    # sampling order = ['day', 'month', 'rain', 'wind', 'FFMC', 'DMC', 'DC', 'ISI']

    cpt_list = []
    # print nodes.index('FFMC')
    for node, parents in zip(nodes, all_parents):
        cpt_list.append(create_cpt(node, node_vals[node], parents, [node_vals[p] for p in parents]))

    sum_result = np.zeros(5)
    result_over_time = np.zeros((7, 5))     # 7 points to check results for convergence
    size = 10001
    for i in range(size):
        w = 1
        day_cpt = cpt_list[nodes.index('day')]
        sample_day = np.random.choice(7, size=1, p=day_cpt)[0]

        month_cpt = cpt_list[nodes.index('month')]
        sample_month = np.random.choice(12, size=1, p=month_cpt)[0]

        rain_cpt = cpt_list[nodes.index('rain')]
        rain_cpt_set = rain_cpt[:, sample_month]
        sample_rain = np.random.choice(5, size=1, p=rain_cpt_set)[0]

        RH_cpt = cpt_list[nodes.index('RH')]
        sample_rh = RH_set
        w *= RH_cpt[RH_set, sample_day]

        temp_cpt = cpt_list[nodes.index('temp')]
        sample_temp = temp_set
        w *= temp_cpt[sample_temp, sample_month]

        wind_cpt = cpt_list[nodes.index('wind')]
        wind_cpt_set = wind_cpt[:, sample_month, sample_day]
        if sum(wind_cpt_set) == 0:
            wind_cpt_set = [0.2, 0.2, 0.2, 0.2, 0.2]
        sample_wind = np.random.choice(5, size=1, p=wind_cpt_set)[0]

        FFMC_cpt = cpt_list[nodes.index('FFMC')]
        FFMC_cpt_set = FFMC_cpt[:, sample_temp, sample_rh, sample_wind, sample_rain]
        if sum(FFMC_cpt_set) == 0:
            FFMC_cpt_set = [0.2, 0.2, 0.2, 0.2, 0.2]
        sample_FFMC = np.random.choice(5, size=1, p=FFMC_cpt_set)[0]


        DMC_cpt = cpt_list[nodes.index('DMC')]
        DMC_cpt_set = DMC_cpt[:, sample_temp, sample_rh, sample_rain]
        if sum(DMC_cpt_set) == 0:
            DMC_cpt_set = [0.2, 0.2, 0.2, 0.2, 0.2]
        sample_DMC = np.random.choice(5, size=1, p=DMC_cpt_set)[0]

        DC_cpt = cpt_list[nodes.index('DC')]
        DC_cpt_set = DC_cpt[:, sample_temp, sample_rain]
        if sum(DC_cpt_set) == 0:
            DC_cpt_set = [0.2, 0.2, 0.2, 0.2, 0.2]
        sample_DC = np.random.choice(5, size=1, p=DC_cpt_set)[0]

        ISI_cpt = cpt_list[nodes.index('ISI')]
        ISI_cpt_set = ISI_cpt[:, sample_FFMC, sample_wind]
        if sum(ISI_cpt_set) == 0:
            ISI_cpt_set = [0.2, 0.2, 0.2, 0.2, 0.2]
        sample_ISI = np.random.choice(5, size=1, p=ISI_cpt_set)[0]

        area_cpt = cpt_list[nodes.index('area')]
        area_cpt_set = area_cpt[:, sample_DMC, sample_DC, sample_ISI]
        if sum(area_cpt_set) == 0:
            area_cpt_set = [0.2, 0.2, 0.2, 0.2, 0.2]
            # area_cpt_set = create_cpt('area', 5, [], [])
        sample_area = np.random.choice(5, size=1, p=area_cpt_set)[0]

        sum_result[sample_area] += w

        if i == 10:
            result_over_time[0, :] = sum_result/float(10)
        elif i == 50:
            result_over_time[1, :] = sum_result / float(50)
        elif i == 100:
            result_over_time[2, :] = sum_result / float(100)
        elif i == 500:
            result_over_time[3, :] = sum_result / float(500)
        elif i == 1000:
            result_over_time[4, :] = sum_result / float(1000)
        elif i == 5000:
            result_over_time[5, :] = sum_result / float(5000)
    result_over_time[6, :] = sum_result / float(10000)
    return result_over_time


if __name__ == '__main__':
    start_time = time.clock()
    # dict_input = {1:0.43453296,  2:0.41274265,  3:0.06350503,  4:0.08287687,  5:0.00634249}
    # plt.bar(range(len(dict_input)), dict_input.values(), align='center')
    # plt.xticks(range(len(dict_input)), dict_input.keys())
    # plt.savefig('./ttt.png')
    # plt.show()
    answers = []
    for rh in range(5):
        for temp in range(5):
            res = forward_sampling(RH_set=rh, temp_set=temp)
            answers.append(res)
            temp_res = [x/float(sum(res[6])) for x in res[6]]
            print 'RH=' + str(rh) + ' temp=' + str(temp) + ': ' + str(temp_res)
    print 'time: ' + str(time.clock()-start_time)
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # x, y = np.random.rand(2, 100) * 10
    # hist, xedges, yedges = np.histogram2d(x, y, bins=5, range=[[0, 4], [0, 4]])
    # print hist
    # print xedges
    # print yedges
    # # Construct arrays for the anchor positions of the 16 bars.
    # # Note: np.meshgrid gives arrays in (ny, nx) so we use 'F' to flatten xpos,
    # # ypos in column-major order. For numpy >= 1.7, we could instead call meshgrid
    # # with indexing='ij'.
    # xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25)
    # xpos = xpos.flatten('F')
    # ypos = ypos.flatten('F')
    # zpos = np.zeros_like(xpos)
    #
    # # Construct arrays with the dimensions for the 16 bars.
    # dx = 0.5 * np.ones_like(zpos)
    # dy = dx.copy()
    # dz = hist.flatten()
    #
    # ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color='b', zsort='average')
    #
    # plt.show()
