import datetime, argparse, json, csv
from dateutil.parser import parse

from tqdm import trange, tqdm
import numpy as np


TABLEDATA = "../data/acs/table_codes_binary.json"
TRIPDATA = "../data/trips/tripcols.json"


def get_type(string):

    if is_date(string): return 'date'
    elif is_bool(string): return 'boolean'
    elif is_float(string): return 'float'
    else: return 'string'


def is_date(string):
    
    if ('AM' in string or 'PM' in string): return True
    else: return False


def is_float(string):

    try: float(string); return True
    except ValueError: return False


def is_bool(string):

    if ('true' in string or 'false' in string): return True
    else: return False


def get_sec_time(dt):
    
    t = dt.time()
    return float(
        datetime.timedelta(
            hours=t.hour, minutes=t.minute,
            seconds=t.second, microseconds=t.microsecond
        ).total_seconds()
    )


def get_column_types(inpath):

    with open(inpath, 'r') as infile: 
        header = infile.readline().strip().split(',')

        line = infile.readline()
        while line:
            line = list(csv.reader([line.strip()]))[0]
            if '' not in line: break
            line = infile.readline()

        tlist = [] 
        for i in range(len(header)):
            tlist.append(get_type(line[i]))

    tlist = np.asarray(tlist)
    return header, tlist


def expand_date_colnames(inpath, tlist):

    with open(inpath, 'r') as infile:

        # Expand header to include new column titles
        header = np.asarray(infile.readline().strip().split(','))
        nheader, ntlist = [], []

        for i in range(len(header)):
            if tlist[i] == 'date': 
                nheader.append('%s %s' % (header[i], 'Month'))
                nheader.append('%s %s' % (header[i], 'Day'))
                nheader.append('%s %s' % (header[i], 'Year'))
                nheader.append('%s %s' % (header[i], 'Time'))

            elif tlist[i] == 'float' or tlist[i] == 'boolean':
                nheader.append(header[i])

    header = np.asarray(nheader)
    return header


def expand_date_colvals(inpath, header, linecount, tlist, limit=None):

    V, D = linecount-1, header.shape[0]
    if limit is not None: V = limit

    data = np.empty((V, D))

    with open(inpath, 'r') as infile:
        infile.readline()
        
        line, ridx = infile.readline(), 0
        progress = tqdm(total=linecount-1, desc='Formatting Columns')

        while ridx < V:
            row = process_line(line, tlist)
            data[ridx] = np.asarray(row)
            line = infile.readline()
            progress.update(1)
            ridx += 1

    return data


def process_line(line, tlist):

    line = list(csv.reader([line.strip()]))[0]

    row = []
    for idx in range(len(line)):
		
        if tlist[idx] == 'float': 
            if line[idx] == '': row.append(None)
            else: row.append(np.float(line[idx]))

        elif tlist[idx] == 'date':
            d = parse(line[idx])
            row += [d.month, d.day, d.year, get_sec_time(d)]

        elif tlist[idx] == 'boolean':
            row.append(0 if line[idx] == 'false' else 1)

    return row


def combine_cols(data, header, tabledata, tables):

    for table in tqdm(tables, desc='Combining Columns'):
        if 'combine' in tabledata[table]:
            for comb in tabledata[table]['combine']:
                pncolname = '%s_PICKUP' % comb
                dncolname = '%s_DROPOFF' % comb

                pcols = ['%s_PICKUP' % col for col in tabledata[table]['combine'][comb]['columns']]
                dcols = ['%s_DROPOFF' % col for col in tabledata[table]['combine'][comb]['columns']]

                pidxs = np.asarray([np.argwhere(header == pcols[idx])[0][0] for idx in range(len(pcols))])
                didxs = np.asarray([np.argwhere(header == dcols[idx])[0][0] for idx in range(len(dcols))])

                pcol = np.nansum(data[:, pidxs], axis=1)
                dcol = np.nansum(data[:, didxs], axis=1)
                pcol = pcol.reshape((pcol.shape[0], 1))
                dcol = dcol.reshape((dcol.shape[0], 1))

                header = np.concatenate([header, [pncolname, dncolname]])
                data = np.concatenate([data, pcol, dcol], axis=1)

    return data, header 


def delete_spare_cols(data, header, tabledata, tables):

    for table in tqdm(tables, desc='Deleting Spare Columns'):
        if 'delete' in tabledata[table]:
            for col in tabledata[table]['delete']:

                pidx = np.argwhere(header == '%s_PICKUP' % col)
                didx = np.argwhere(header == '%s_DROPOFF' % col)

                dargs = np.delete(np.arange(data.shape[1]), [pidx, didx])
                header = header[dargs]
                data = data[:, dargs]

    return data, header


def replace_nans(data):

    V, D = data.shape
    for cidx in trange(D, desc='Replacing NaNs'):
        nans = (np.isnan(data[:, cidx])).any()
        if nans: 
            nargs = np.where(np.isnan(data[:, cidx]))[0]
            data[nargs, cidx] = np.nanmean(data[:, cidx])

    return data


def delete_spare_trip_cols(data, header, tripdata):

    delcols = []
    for col in tqdm(header, desc='Deleting Spare Columns'):
        if col in tripdata["columns"]:
            if col not in tripdata["keep"]:
                delcols.append(col)
    
    dargs = np.asarray([np.argwhere(header == col)[0][0] for col in delcols])
    dargs = np.delete(np.arange(data.shape[1]), dargs)
    header = header[dargs]
    data = data[:, dargs]

    return data, header


def add_commute_time_marker(data, header):

    ptime = np.argwhere(header == 'Trip Start Timestamp Time')[0, 0]
    dtime = np.argwhere(header == 'Trip End Timestamp Time')[0, 0]

    mstart = datetime.timedelta(hours=7).total_seconds()
    mend = datetime.timedelta(hours=9).total_seconds()
    estart = datetime.timedelta(hours=16).total_seconds()
    eend = datetime.timedelta(hours=18).total_seconds()

    mr1 = np.argwhere(data[:, ptime] >= mstart).flatten()
    mr2 = np.argwhere(data[:, dtime] <= mend).flatten()
    mrows = np.intersect1d(mr1, mr2)
    morning = np.zeros((data.shape[0], 1))
    morning[mrows] = 1

    er1 = np.argwhere(data[:, ptime] >= estart).flatten()
    er2 = np.argwhere(data[:, dtime] <= eend).flatten()
    erows = np.intersect1d(er1, er2)
    evening = np.zeros((data.shape[0], 1))
    evening[erows] = 1

    header = np.concatenate([header, ['Morning', 'Evening']])
    data = np.concatenate([data, morning, evening], axis=1)

    return data, header


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-m', '--metapath', type=str, required=True)
    args = parser.parse_args()
    inpath, outpath, metapath = args.input, args.output, args.metapath

    with open(inpath, 'r') as infile: linecount = sum(1 for line in infile)
    with open(TABLEDATA, 'r') as infile: tabledata = json.load(infile)
    with open(metapath, 'r') as infile: tripdata = json.load(infile)

    tables = sorted(list(tabledata.keys()))

    # Determine type of each column
    header, tlist = get_column_types(inpath)

    # Expand all date column names
    header = expand_date_colnames(inpath, tlist)

    # Expand datetime column values
    data = expand_date_colvals(inpath, header, linecount, tlist)

    # Combine columns as specified in the table codes file
    data, header = combine_cols(data, header, tabledata, tables)

    # Delete rideshare columns as specified in the table codes file
    data, header = delete_spare_cols(data, header, tabledata, tables)

    # Combine/Delete columns as specified in the rideshare data file
    data, header = delete_spare_trip_cols(data, header, tripdata)

    # Add marker columns for morning and evening commute
    data, header = add_commute_time_marker(data, header)

    np.savetxt(outpath, data, fmt='%0.8f', delimiter=',', header=','.join(header), comments='')



if __name__ == '__main__':
    main()
