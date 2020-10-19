import json

import numpy as np


METAPATH = '../data/ricci_meta.json'
DATAPATH = '../data/ricci_raw.data'
OUTPATH = '../data/ricci_clean.csv'


def main():

    header = np.asarray([item.strip('"') for item in np.loadtxt(DATAPATH, delimiter=',', dtype=str, max_rows=1)])
    data = np.loadtxt(DATAPATH, delimiter=',', dtype=str, skiprows=1)
    with open(METAPATH, 'r') as infile: meta = json.load(infile)

    ndata = []
    for idx in range(len(meta)):
        if meta[idx]['type'] == 'float':
            ncol = np.asarray([item.strip('"') for item in data[:, idx]]).astype(np.float64)

        elif meta[idx]['type'] == 'string':
            col = np.asarray([item.strip('"') for item in data[:, idx]])
            ncol = []

            for ridx in range(col.shape[0]):
                ncol.append(meta[idx]['vals'][col[ridx]])

        ndata.append(np.asarray(ncol).reshape((-1, 1)))

    data = np.concatenate(ndata, axis=1)

    passed = np.zeros((data.shape[0], 1))
    pargs = np.argwhere(data[:, np.argwhere(header=='Combine')[0, 0]] >= 70).flatten()
    passed[pargs] = 1

    data = np.concatenate([data, passed], axis=1)
    header = np.concatenate([header, ['Passed']])

    np.savetxt(OUTPATH, data, fmt='%0.8f', delimiter=',', header=','.join(header), comments='')


if __name__ == '__main__':
    main()
