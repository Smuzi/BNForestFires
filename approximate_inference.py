import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas


if __name__ == '__main__':
    # dict_input = {1:0.43453296,  2:0.41274265,  3:0.06350503,  4:0.08287687,  5:0.00634249}
    # plt.bar(range(len(dict_input)), dict_input.values(), align='center')
    # plt.xticks(range(len(dict_input)), dict_input.keys())
    # plt.savefig('./ttt.png')
    # plt.show()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x, y = np.random.rand(2, 100) * 10
    hist, xedges, yedges = np.histogram2d(x, y, bins=5, range=[[0, 4], [0, 4]])
    print hist
    print xedges
    print yedges
    # Construct arrays for the anchor positions of the 16 bars.
    # Note: np.meshgrid gives arrays in (ny, nx) so we use 'F' to flatten xpos,
    # ypos in column-major order. For numpy >= 1.7, we could instead call meshgrid
    # with indexing='ij'.
    xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25)
    xpos = xpos.flatten('F')
    ypos = ypos.flatten('F')
    zpos = np.zeros_like(xpos)

    # Construct arrays with the dimensions for the 16 bars.
    dx = 0.5 * np.ones_like(zpos)
    dy = dx.copy()
    dz = hist.flatten()

    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color='b', zsort='average')

    plt.show()
