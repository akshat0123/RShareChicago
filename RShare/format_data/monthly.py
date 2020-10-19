import argparse, json

from tqdm import trange, tqdm
import numpy as np


TABLEDATA = "../data/acs/table_codes_binary.json"


def get_header_titles(header, tdata):

    nheader = []
    for col in header:
        cids = col.split('_')

        if len(cids) == 1:
            nheader.append(col)

        if len(cids) == 2:
            tablename = cids[0][:6]
            colname = cids[0]
            nheader.append('%s (%s)' % (tdata[tablename]["columns"][colname]["column_title"], cids[1].lower()))

        elif len(cids) == 3:
            tablename = cids[0][:6]
            colname = '_'.join(cids[:2])
            nheader.append('%s (%s)' % (tdata[tablename]["combine"][colname]["column_title"], cids[2].lower()))

    return np.asarray(nheader)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    args = parser.parse_args()
    inpath, outdir = args.input, args.output

    with open(TABLEDATA, 'r') as infile: tdata = json.load(infile)

    header = np.loadtxt(inpath, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(inpath, delimiter=',', skiprows=1)
    titles = get_header_titles(header, tdata)

    midx = np.argwhere(header=='Trip Start Timestamp Month')[0, 0]
    yidx = np.argwhere(header=='Trip Start Timestamp Year')[0, 0]
    months = np.unique(data[:, midx])
    years = np.unique(data[:, yidx])

    for year in years:
        for month in tqdm(months, desc='Splitting Data by Months'):
            mdata = data[(data[:, midx] == month) & (data[:, yidx] == year)]

            if mdata.shape[0] > 0:
                opath = '%s%d_%d_%s' % (outdir, year, month, inpath.split('/')[-1])
                np.savetxt(opath, mdata, fmt='%0.8f', delimiter=',', header=','.join(header), comments='')


if __name__ == '__main__':
    main()
