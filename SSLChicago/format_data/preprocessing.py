import json

from tqdm import tqdm
import numpy as np


OUTPATH = '../data/Strategic_Subject_List_preprocessed.csv'
DATAPATH = '../data/Strategic_Subject_List_merged.csv'
TABLEDATA = '../data/table_codes_binary.json'


def main():

    with open(TABLEDATA, 'r') as infile: tabledata = json.load(infile)
    header = np.loadtxt(DATAPATH, delimiter=',', dtype=str, max_rows=1)
    data = np.loadtxt(DATAPATH, delimiter=',', skiprows=1)

    tables = sorted(list(tabledata.keys()))
    for table in tqdm(tables, desc='Combining Columns'):
        for col in sorted(tabledata[table]['combine']):
            ccols = sorted(tabledata[table]['combine'][col]['columns'])
            ccargs = np.asarray([np.argwhere(header == ccol)[0, 0] for ccol in ccols])
            combined = np.nansum(data[:, ccargs], axis=1).reshape((-1, 1))

            header = np.concatenate([header, [col]])
            data = np.concatenate([data, combined], axis=1)

    for table in tqdm(tables, desc='Deleting Columns'):
        dcols = tabledata[table]['delete']
        dargs = np.asarray([np.argwhere(header == dcol)[0, 0] for dcol in dcols])
        dargs = np.delete(np.arange(header.shape[0]), dargs)
        header = header[dargs]
        data = data[:, dargs]

    for table in tqdm(tables, desc='Renaming Columns'):
        for col in tabledata[table]['columns']:
            if col in header:
                ncol = tabledata[table]['columns'][col]['column_title']
                carg = np.argwhere(header == col)[0, 0]
                header[carg] = ncol

        for col in tabledata[table]['combine']:
            if col in header:
                ncol = tabledata[table]['combine'][col]['column_title']
                carg = np.argwhere(header == col)[0, 0]
                header[carg] = ncol

    np.savetxt(OUTPATH, data, fmt='%0.8f', delimiter=',', header=','.join(header), comments='')


if __name__ == '__main__':
    main()
