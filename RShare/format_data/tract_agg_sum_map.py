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
    parser.add_argument('-k', '--kind', type=str, required=True)
    parser.add_argument('--morning_only', action='store_true')
    parser.add_argument('--evening_only', action='store_true')
    args = parser.parse_args()
    inpath, outpath, dtype, monly, eonly = args.input, args.output, args.kind, args.morning_only, args.evening_only

    with open(TABLEDATA, 'r') as infile: tdata = json.load(infile)

    header = np.loadtxt(inpath, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(inpath, delimiter=',', skiprows=1)
    titles = get_header_titles(header, tdata)

    if monly: 
        mcol = np.argwhere(titles == 'Morning')[0, 0]
        data = data[np.argwhere(data[:, mcol] == 1).flatten(), :]

    if eonly:
        mcol = np.argwhere(titles == 'Evening')[0, 0]
        data = data[np.argwhere(data[:, mcol] == 1).flatten(), :]

    if dtype == 'Rideshare':
        sidx = np.argwhere(titles == "Shared Trip Authorized")[0, 0]
        srows = np.argwhere(data[:, sidx] == 1).flatten()
        srows = np.delete(np.arange(data.shape[0]), srows)
        data = data[srows]

    # Add fare per mile and fare per second columns
    fare_col = np.argwhere(header == "Fare")[0, 0]
    mi_col = np.argwhere(header == "Trip Miles")[0, 0]
    sec_col = np.argwhere(header == "Trip Seconds")[0, 0]

    dcols = np.argwhere(data[:, fare_col] == 0.0).flatten()
    dcols = np.delete(np.arange(data.shape[0]), dcols)
    data = data[dcols]

    dcols = np.argwhere(data[:, mi_col] == 0.0).flatten()
    dcols = np.delete(np.arange(data.shape[0]), dcols)
    data = data[dcols]

    dcols = np.argwhere(data[:, sec_col] == 0.0).flatten()
    dcols = np.delete(np.arange(data.shape[0]), dcols)
    data = data[dcols]

    dcols = np.argwhere(np.isnan(data[:, fare_col])).flatten()
    dcols = np.delete(np.arange(data.shape[0]), dcols)
    data = data[dcols]

    dcols = np.argwhere(np.isnan(data[:, mi_col])).flatten()
    dcols = np.delete(np.arange(data.shape[0]), dcols)
    data = data[dcols]

    dcols = np.argwhere(np.isnan(data[:, sec_col])).flatten()
    dcols = np.delete(np.arange(data.shape[0]), dcols)
    data = data[dcols]

    fare_per_mi = (data[:, fare_col] / data[:, mi_col]).reshape((data.shape[0], 1))
    fare_per_sec = (data[:, sec_col] / data[:, sec_col]).reshape((data.shape[0], 1))
    sec_per_mi = (data[:, sec_col] / data[:, mi_col]).reshape((data.shape[0], 1))

    header = np.concatenate([header, ["Fare/Mi", "Fare/Sec", "Sec/Mi"]])
    titles = np.concatenate([titles, ["Fare/Mi", "Fare/Sec", "Sec/Mi"]])
    data = np.concatenate([data, fare_per_mi], axis=1)
    data = np.concatenate([data, fare_per_sec], axis=1)
    data = np.concatenate([data, sec_per_mi], axis=1)

    # Separate Census data from rideshare trip data (except fare/mi & fare/sec columns)
    pargs = np.asarray([np.argwhere(header == item)[0][0] for item in header if ('_PICKUP' in item or item == 'Pickup Census Tract')])
    dargs = np.asarray([np.argwhere(header == item)[0][0] for item in header if ('_DROPOFF' in item or item == 'Dropoff Census Tract')])
    p_idx = np.argwhere(titles == "Pickup Census Tract")[0][0]
    d_idx = np.argwhere(titles == "Dropoff Census Tract")[0][0]
    fpm_idx = np.argwhere(titles == "Fare/Mi")[0][0]
    fps_idx = np.argwhere(titles == "Fare/Sec")[0][0]
    spm_idx = np.argwhere(titles == "Sec/Mi")[0][0]
    mr_idx = np.argwhere(titles == "Morning")[0][0]
    er_idx = np.argwhere(titles == "Evening")[0][0]
    ptitles, dtitles = titles[pargs], titles[dargs]

    # Aggregate data for all tracts
    trows, pcounts, dcounts, pfmi, pfs, psm, dfmi, dfs, dsm = {}, {}, {}, {}, {}, {}, {}, {}, {}
    mrpcounts, mrdcounts = {}, {}
    erpcounts, erdcounts = {}, {}
    for idx in trange(data.shape[0]):
        pickup = data[idx, pargs]
        dropoff = data[idx, dargs]
        ptract = data[idx, p_idx]
        dtract = data[idx, d_idx]
        fmi = data[idx, fpm_idx]
        fps = data[idx, fps_idx]
        spm = data[idx, spm_idx]
        mr = data[idx, mr_idx]
        er = data[idx, er_idx]

        if ptract not in trows: trows[ptract] = pickup[1:]
        if dtract not in trows: trows[dtract] = dropoff[1:]

        # Count number of rides in pickup tract
        if ptract in pcounts: pcounts[ptract] += 1
        else: pcounts[ptract] = 1

        # Count number of rides in dropoff tract
        if dtract in dcounts: dcounts[dtract] += 1
        else: dcounts[dtract] = 1

        # Add fare per mile for each ride in pickup tract
        if ptract in pfmi: pfmi[ptract] += fmi
        else: pfmi[ptract] = fmi

        # Add fare per second for each ride in pickup tract
        if ptract in pfs: pfs[ptract] += fps
        else: pfs[ptract] = fps

        # Add second per mile for each ride in pickup tract
        if ptract in psm: psm[ptract] += spm
        else: psm[ptract] = spm

        # Add fare per mile for each ride in dropoff tract
        if dtract in dfmi: dfmi[dtract] += fmi
        else: dfmi[dtract] = fmi

        # Add fare per second for each ride in dropoff tract
        if dtract in dfs: dfs[dtract] += fps
        else: dfs[dtract] = fps

        # Add second per mile for each ride in dropoff tract
        if dtract in dsm: dsm[dtract] += spm
        else: dsm[ptract] = spm

        # Count number of rides in morning rush hour pickup tract
        if ptract in mrpcounts: mrpcounts[ptract] += mr
        else: mrpcounts[ptract] = mr

        # Count number of rides in morning rush hour dropoff tract
        if dtract in mrdcounts: mrdcounts[dtract] += mr
        else: mrdcounts[dtract] = mr

        # Count number of rides in evening rush hour pickup tract
        if ptract in erpcounts: erpcounts[ptract] += er
        else: erpcounts[ptract] = er

        # Count number of rides in evening rush hour dropoff tract
        if dtract in erdcounts: erdcounts[dtract] += er
        else: erdcounts[dtract] = er

    tracts = list(trows.keys())
    header = np.asarray([item.strip("(pickup)").strip().replace(',', '') for item in ptitles] + ['Pickup Count', 'Dropoff Count', 'Pickup Fare/Mi', 'Pickup Fare/Sec', 'Pickup Sec/Mi', 'Dropoff Fare/Mi', 'Dropoff Fare/Sec', 'Dropoff Sec/Mi', 'Pickup_MRush', 'Pickup_ERush', 'Dropoff_MRush', 'Dropoff_ERush'])
    header[0] = 'Census Tract'

    data = []
    for tract in tracts:
        if tract in trows:
            row = np.concatenate([[tract], trows[tract]])

            if tract in pcounts: row = np.concatenate([row, [pcounts[tract]]])
            else: row = np.concatenate([row, [0]])

            if tract in dcounts: row = np.concatenate([row, [dcounts[tract]]])
            else: row = np.concatenate([row, [0]])

            if tract in pfmi: row = np.concatenate([row, [pfmi[tract]]])
            else: row = np.concatenate([row, [0]])

            if tract in pfs: row = np.concatenate([row, [pfs[tract]]])
            else: row = np.concatenate([row, [0]])

            if tract in psm: row = np.concatenate([row, [psm[tract]]])
            else: row = np.concatenate([row, [0]])

            if tract in dfmi: row = np.concatenate([row, [dfmi[tract]]])
            else: row = np.concatenate([row, [0]])

            if tract in dfs: row = np.concatenate([row, [dfs[tract]]])
            else: row = np.concatenate([row, [0]])

            if tract in dsm: row = np.concatenate([row, [dsm[tract]]])
            else: row = np.concatenate([row, [0]])

            if tract in mrpcounts: row = np.concatenate([row, [mrpcounts[tract]]])
            else: row = np.concatenate([row, [0]])

            if tract in erpcounts: row = np.concatenate([row, [erpcounts[tract]]])
            else: row = np.concatenate([row, [0]])

            if tract in mrdcounts: row = np.concatenate([row, [mrdcounts[tract]]])
            else: row = np.concatenate([row, [0]])

            if tract in erdcounts: row = np.concatenate([row, [erdcounts[tract]]])
            else: row = np.concatenate([row, [0]])

            data.append(row)

    data = np.asarray(data).astype(np.float64)
    np.savetxt(outpath, data, delimiter=',', fmt='%0.8f', header=','.join(header), comments='') 


if __name__ == "__main__":
    main()
