import argparse

from tqdm import trange, tqdm
import numpy as np


DATAPATH = '../data/Strategic_Subject_List_preprocessed.csv'


def main():

    target = 'SSL SCORE' 
    header = np.loadtxt(DATAPATH, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(DATAPATH, delimiter=',', skiprows=1)

    ridx = np.argwhere(header=="RACE CODE CD")[0, 0]
    data[np.argwhere(data[:, ridx]!=4), ridx] = 1
    data[np.argwhere(data[:, ridx]==4), ridx] = 0

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

    cidx = np.argwhere(header=="Non-White Percentage")[0, 0]
    tidx = np.argwhere(header==target)[0, 0]

    att, att_maj = "RACE CODE CD", 0 
    aidx = np.argwhere(header==att)[0, 0]

    # Calculate effect size on protected attributes
    print('Bias Score on Protected Attributes')
    majargs = np.argwhere(data[:, aidx]==att_maj)[0, 0]
    minargs = np.argwhere(data[:, aidx]!=att_maj)[0, 0]
    majval = np.mean(data[majargs, tidx])
    minval = np.mean(data[minargs, tidx])
    std = np.std(data[:, tidx])
    es = np.abs((majval - minval)/std)
    print(es)
    print()


if __name__ == '__main__':
    main()
