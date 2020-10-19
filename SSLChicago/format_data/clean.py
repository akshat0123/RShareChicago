import datetime, json, csv

from tqdm import trange, tqdm
import numpy as np


OUTPATH = '../data/Strategic_Subject_List_clean.csv'
DATAPATH = '../../Data/Strategic_Subject_List.csv'
METAPATH = '../data/Strategic_Subject_List.json'


def get_sec_time(time):

    t = datetime.datetime.strptime(time, '%H:%M:%S').time()

    secs = float(
        datetime.timedelta(
            hours=t.hour, minutes=t.minute,
            seconds=t.second, microseconds=t.microsecond
        ).total_seconds()
    )

    return secs


def get_relevant_idxs(header, meta):

    cidxs = []
    for col in header:
        if meta[col]['keep']:
            cidxs.append(np.argwhere(header == col)[0, 0])

    return np.asarray(cidxs)


def expand_cols(header, meta):

    nheader = []
    for title in header:
        if meta[title]['keep']: 

            if meta[title]['type'] == 'string':
                if meta[title]['one_hot']:
                    for value in meta[title]['values']:
                        nheader.append('%s_%s' % (title, value.replace(' ', '_')))

                else: nheader.append(title)
            else: nheader.append(title)

    return np.asarray(nheader)


def process_line(nheader, header, meta, cidxs, row):

    row = np.asarray(row)[cidxs]
    nrow = np.zeros(nheader.shape[0])

    for idx, item in enumerate(row):
        dtype = meta[header[idx]]['type']

        if dtype == 'string':
            if meta[header[idx]]['one_hot']:
                val = '%s_%s' % (header[idx], row[idx].replace(' ', '_'))
                varg = np.argwhere(nheader == val)[0, 0]
                nrow[varg] = 1

            else:
                varg = np.argwhere(nheader == header[idx])

                if row[idx] == '': nrow[varg] = np.NaN
                else: nrow[varg] = meta[header[idx]]["values"][row[idx]]

        elif dtype == 'float':
            varg = np.argwhere(nheader == header[idx])

            if row[idx] == '': nrow[varg] = np.NaN
            else: nrow[varg] = np.float64(row[idx])

        elif dtype == 'time':
            varg = np.argwhere(nheader == header[idx])

            if row[idx] == '': nrow[varg] = np.NaN
            else: nrow[varg] = get_sec_time(row[idx])

        elif dtype == 'boolean':
            varg = np.argwhere(nheader == header[idx])

            if row[idx] == '': nrow[varg] = np.NaN
            elif row[idx] == 'N': nrow[varg] = 0
            elif row[idx] == 'Y': nrow[varg] = 1
            
                
    return nrow


def main():

    with open(DATAPATH, 'r') as infile: linecount = sum([1 for line in infile])
    with open(METAPATH, 'r') as infile: meta = json.load(infile)

    header = np.loadtxt(DATAPATH, dtype=str, delimiter=',', max_rows=1)
    cidxs = get_relevant_idxs(header, meta)
    header = header[cidxs]

    nheader = expand_cols(header, meta)

    data = np.empty((linecount-1, nheader.shape[0]))
    with open(DATAPATH, 'r') as infile:
        reader = csv.reader(infile, delimiter=',')
        next(reader)

        idx = 0
        progress = tqdm(total=linecount)
        for row in reader:

            line = process_line(nheader, header, meta, cidxs, row)
            data[idx] = line
            idx += 1

            progress.update(1)

    np.savetxt(OUTPATH, data, fmt='%0.8f', delimiter=',', header=','.join(nheader), comments='')



if __name__ == '__main__': 
    main()
