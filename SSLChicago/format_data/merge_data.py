import json

from tqdm import tqdm
import numpy as np


DATAPATH = '../data/Strategic_Subject_List_clean.csv'
OUTPATH = '../data/Strategic_Subject_List_merged.csv'
TABLEDATA = '../data/table_codes_binary.json'
TRACTDATA = '../../Data/tract_data.json'

def main():

    with open(TABLEDATA, 'r') as infile: tabledata = json.load(infile)
    with open(TRACTDATA, 'r') as infile: tractdata = json.load(infile)

    header = np.loadtxt(DATAPATH, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(DATAPATH, delimiter=',', skiprows=1)

    tables = sorted(tabledata.keys())

    cols = {}
    for table in tables:
        cols[table] = sorted(list(tabledata[table]['columns'].keys()))

    nheader = []
    for table in tables:
        for col in cols[table]: nheader.append(col)

    nheader = np.asarray(nheader)
    nheader = np.concatenate([header, nheader])

    nrows = [np.argwhere(np.isnan(data[:, cidx])).flatten() for cidx in range(header.shape[0])]
    nrows = np.unique(np.concatenate(nrows))
    nrows = np.delete(np.arange(data.shape[0]), nrows)
    data = data[nrows, :]

    tidx = np.argwhere(header == 'CENSUS TRACT')[0, 0]

    ndata = []
    for row in tqdm(data):
        tract = str(int(row[tidx])).zfill(11)

        if tract in tractdata:

            nrow = []
            for table in tables:
                for col in cols[table]:
                    nrow.append(tractdata[tract][table]['estimate'][col])

            nrow = np.asarray(nrow)
            row = np.concatenate([row, nrow])
            ndata.append(row)

    data = np.asarray(ndata)
    np.savetxt(OUTPATH, data, fmt='%0.8f', delimiter=',', header=','.join(nheader), comments='')


if __name__ == '__main__':
    main()
