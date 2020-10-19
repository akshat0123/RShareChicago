import argparse, json

from tqdm import tqdm
import numpy as np


TABLEDATA = "../data/acs/table_codes_binary.json"
TRACTDATA = "../../Data/tract_data.json"
TRACTS = "../data/acs/tracts.csv"


def get_acs_data(tract, tractdata, tables, cols, tcache, flag=None):

    if tract in tcache: row = tcache[tract]

    else: 

        row = []
        for table in tables:
            for col in cols[table]:

                if tract != '': 

                    if not flag:
                        row.append(str(tractdata[tract][table]['estimate'][col]))

                    elif flag == 'min':
                        row.append(
                            str(
                                tractdata[tract][table]['estimate'][col] -
                                tractdata[tract][table]['error'][col]
                            )
                        )

                    elif flag == 'max':
                        row.append(
                            str(
                                tractdata[tract][table]['estimate'][col] +
                                tractdata[tract][table]['error'][col]
                            )
                        )

                else: row.append('')
        
        tcache[tract] = row

    return row


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('--min', action='store_true')
    parser.add_argument('--max', action='store_true')
    args = parser.parse_args()
    inpath, outpath, dmin, dmax = args.input, args.output, args.min, args.max

    with open(TRACTS, 'r') as infile: tracts = [line.strip() for line in infile.readlines()]
    with open(TABLEDATA, 'r') as infile: tabledata = json.load(infile)
    with open(TRACTDATA, 'r') as infile: tractdata = json.load(infile)

    tables = sorted(tabledata.keys())
    tracts = sorted(tracts)

    cols = {}
    for table in tables:
        cols[table] = sorted(list(tabledata[table]['columns'].keys()))

    with open(inpath, 'r') as infile: header = np.asarray(infile.readline().strip().split(','))
    ptract_idx = np.argwhere(header == 'Pickup Census Tract')[0, 0]
    dtract_idx = np.argwhere(header == 'Dropoff Census Tract')[0, 0]

    pcols, dcols = [], []
    for table in tables:
        for col in cols[table]:
            pcols.append("%s_PICKUP" % col)
            dcols.append("%s_DROPOFF" % col)
    header = np.concatenate([header, pcols, dcols])

    with open(outpath, 'w') as outfile: outfile.write('%s\n' % ','.join(header))

    with open(inpath, 'r') as infile: linecount = sum(1 for line in infile)
    progress = tqdm(total=linecount)
    tcache = {}

    # Merge rideshare data with ACS data
    with open(outpath, 'a') as outfile:
        with open(inpath, 'r') as infile:

            infile.readline()
            line = infile.readline()
            progress.update(1)

            while line:
                row = line.strip().split(',')
                ptract, dtract = row[ptract_idx], row[dtract_idx]

                if ptract != '' and dtract != '':
                    
                    if dmin:
                        row += get_acs_data(ptract, tractdata, tables, cols, tcache, flag='min')
                        row += get_acs_data(dtract, tractdata, tables, cols, tcache, flag='min')

                    elif dmax:
                        row += get_acs_data(ptract, tractdata, tables, cols, tcache, flag='max')
                        row += get_acs_data(dtract, tractdata, tables, cols, tcache, flag='max')

                    else:
                        row += get_acs_data(ptract, tractdata, tables, cols, tcache)
                        row += get_acs_data(dtract, tractdata, tables, cols, tcache)

                    outfile.write('%s\n' % ','.join(row))

                line = infile.readline()
                progress.update(1)
        

if __name__ == '__main__':
    main()
