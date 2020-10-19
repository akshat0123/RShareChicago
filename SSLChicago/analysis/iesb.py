import matplotlib.patches as mpatches
from scipy.stats import linregress
import matplotlib.pyplot as plt
from scipy.stats import entropy
from numba import prange, njit
from tqdm import trange, tqdm
import seaborn as sns
from tqdm import tqdm
import numpy as np


DATAPATH = '../data/Strategic_Subject_List_tract_agg.csv'


def combine_columns(data, header, col1, col2):

    c1i = np.argwhere(header == col1)[0, 0]
    c2i = np.argwhere(header == col2)[0, 0]
    c1perc = np.nan_to_num(data[:, c1i] / (data[:, c1i] + data[:, c2i]))
    c1perc = c1perc.reshape((c1perc.shape[0], 1))
    data = np.concatenate([data, c1perc], axis=1)
    header = np.concatenate([header, ['%s Percentage' % (col1)]])
    data = np.delete(data, [c1i, c2i], axis=1)
    header = np.delete(header, [c1i, c2i])

    return data, header 


def calc_percent_rule(x, y, titles, col, minp, maxp):

    cidx = np.argwhere(titles == col)[0, 0]
    rows = np.argwhere((x[:, cidx] >= minp) & (x[:, cidx] < maxp))
    y = y[rows].flatten()

    return y


def effect_size(y, y1, y2):

    y1mn = np.mean(y1)
    y2mn = np.mean(y2)
    ystd = np.std(y)

    return (y1mn - y2mn) / ystd


def calc_effect_sizes(data, tidx):

    target = data[:, tidx]

    eslist = np.zeros((target.shape[0]-100, ))
    for ridx in trange(50, target.shape[0]-50):
        nrval = np.mean(target[ridx:])
        rval = np.mean(target[:ridx])
        eslist[ridx-50] = rval - nrval

    return eslist


def main():

    target = 'SSL SCORE' 
    header = np.loadtxt(DATAPATH, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(DATAPATH, delimiter=',', skiprows=1)

    tpcol = (
        data[:, np.argwhere(header=="Non-White")[0, 0]] + 
        data[:, np.argwhere(header=="White alone")[0, 0]]
    ).reshape((-1, 1))
    data = np.concatenate([data, tpcol], axis=1)

    header = np.concatenate([header, ['Total']])
    data[:, -1] /= np.sum(data[:, -1])

    colpairs = [
        ["Non-White", "White alone"]
    ]

    added_header = []
    added_cols = []
    for pair in tqdm(colpairs):
        keep = pair[0]
        kidx = np.argwhere(header==keep)[0, 0]
        tidx = np.argwhere(header=='Total')[0, 0]
        col = (data[:, kidx] / data[:, tidx]).reshape((-1, 1))
        added_header.append('%s Percentage' % keep)
        added_cols.append(col)

    header = np.concatenate([header, added_header])
    added_cols = np.hstack(added_cols)
    data = np.concatenate([data, added_cols], axis=1)

    for pair in tqdm(colpairs):
        c1, c2 = pair

        c1idx = np.argwhere(header==c1)[0, 0]
        dargs = np.delete(np.arange(header.shape[0]), c1idx)
        header = header[dargs]
        data = data[:, dargs]

        c2idx = np.argwhere(header==c2)[0, 0]
        dargs = np.delete(np.arange(header.shape[0]), c2idx)
        header = header[dargs]
        data = data[:, dargs]

    # for col1, col2 in tqdm(colpairs): data, header = combine_columns(data, header, col1, col2) 

    cidx = np.argwhere(header=="Non-White Percentage")[0, 0]
    tidx = np.argwhere(header==target)[0, 0]
    data[:, tidx] /= 500

    data = data[~np.isnan(data[:, cidx]), :]

    # Calculate my bias score on census data
    cargs = np.argsort(data[:, cidx])
    data = data[cargs]

    eslist, var_ds = [], []
    std = np.std(data[:, tidx])
    for ridx in range(1, data.shape[0]-1):
        nrval = np.mean(data[ridx:, tidx])
        rval = np.mean(data[:ridx, tidx])
        d = (rval - nrval) / std
        eslist.append(d)

        n1, n2 = ridx, data.shape[0]-ridx

        var_d = (
            (
                ( (n1 + n2) / (n1 * n2) ) +
                ( (d**2) / (2 * (n1 + n2 - 2)) )
            ) * (
                (n1 + n2) / (n1 + n2 - 2)
            )
        )

        var_ds.append(var_d)

    eslist = np.asarray(eslist)
    var_ds = np.asarray(var_ds)
    var_all = np.var(eslist)
    var = var_ds + var_all

    slope, intercept, r_value, p_value, std_err = linregress(
        np.arange(len(eslist)),
        eslist
    )
    slope = '+' if slope >= 0 else '-'

    wmean = np.sum(eslist * (var)) / np.sum(var)
    print(np.abs(wmean), slope)


if __name__ == '__main__':
    main()
