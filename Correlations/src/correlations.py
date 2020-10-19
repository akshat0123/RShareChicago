import csv

from scipy.stats import pearsonr
from tqdm import trange, tqdm
import pandas as pd
import numpy as np


INPATH = '../data/data.csv'
OUTPATH = '../data/correlations.csv'


def main():

    csvreader = csv.reader(open(INPATH, 'r'), delimiter=',')
    data = [line for line in csvreader]
    header, data = np.asarray(data[0])[1:], np.asarray(data[1:]).astype(np.float64)[:, 1:]

    prs = np.zeros((header.shape[0], header.shape[0]))
    pvals = np.zeros((header.shape[0], header.shape[0]))

    pairs = []
    for aidx in trange(header.shape[0]):

        row = []
        for bidx in range(header.shape[0]):

            ndata = np.copy(data)
            kargs = np.argwhere(ndata[:, aidx] != -1).flatten()
            ndata = ndata[kargs]
            kargs = np.argwhere(ndata[:, bidx] != -1).flatten()
            ndata = ndata[kargs]

            pr, pval = pearsonr(ndata[:, aidx], ndata[:, bidx])
            prs[aidx][bidx] = pr
            pvals[aidx][bidx] = pval
            row.append('%0.4f p=%0.4f' % (pr, pval))

        pairs.append(row)

    pairs = pd.DataFrame(pairs)
    pairs.columns = header
    pairs.index = header

    pairs.to_csv(OUTPATH)


if __name__ == '__main__':
    main()
