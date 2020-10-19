import json

import numpy as np


METAPATH = '../data/german_meta.json'
DATAPATH = '../data/german_raw.data'
OUTPATH = '../data/german_clean.csv'


def main():

    with open(METAPATH, 'r') as infile: meta = json.load(infile)
    header = np.asarray([i['title'] for i in meta])
    data = np.loadtxt(DATAPATH, dtype=str)

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

    yo = np.zeros((data.shape[0], 1))
    aidx = np.argwhere(header=='Age in years')[0, 0]
    oargs = np.argwhere(data[:, aidx]>25).flatten()
    yo[oargs] = 1

    header = np.concatenate([header, ['Young/Old']])
    data = np.concatenate([data, yo], axis=1)

    np.savetxt(OUTPATH, data, fmt='%0.8f', delimiter=',', header=','.join(header), comments='')


if __name__ == '__main__':
    main()
