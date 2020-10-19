import argparse

from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
from scipy.stats import zscore
import numpy as np


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    args = parser.parse_args()
    inpath, outpath = args.input, args.output

    header = np.loadtxt(inpath, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(inpath, delimiter=',', skiprows=1)

    fidx = np.argwhere(header == 'Fare')[0, 0]
    midx = np.argwhere(header == 'Trip Miles')[0, 0]

    data = data[np.argwhere(data[:, fidx] > 0.0).flatten(), :]
    data = data[np.argwhere(data[:, midx] > 0.0).flatten(), :]

    fare_per_mi = (data[:, fidx] / data[:, midx]).reshape((-1, 1))
    
    gm = GaussianMixture(n_components=2)
    res = gm.fit_predict(fare_per_mi)

    rargs = np.argwhere(res == 0).flatten()
    data = data[rargs]

    np.savetxt(outpath, data, fmt='%0.8f', delimiter=',', header=','.join(header), comments='')



if __name__ == '__main__':
    main()
