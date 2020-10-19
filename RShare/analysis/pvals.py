import argparse, json

from scipy.stats import linregress
import matplotlib.pyplot as plt
from tqdm import trange, tqdm
import numpy as np


TRACTS = '../../Data/tract_geo_data.json'


def calc_iesbs(data, header, target, pickup=False):

    tracts = json.load(open(TRACTS, 'r'))
    pdict = { tract: tracts[tract]['properties']['population'] for tract in tracts }
    adict = { tract: tracts[tract]['properties']['aland'] for tract in tracts }

    # Remove rows with any NaN values
    nanrows = np.asarray([idx for idx in range(data.shape[0]) if np.isnan(data[idx, :]).any()])
    if nanrows.shape[0] > 0: data = np.delete(data, nanrows, axis=0)

    zrows = np.argwhere(data[:, np.argwhere(header == target)[0, 0]] == 0).flatten()
    data = np.delete(data, zrows, axis=0)

    colpairs = [
        ["Non-White", "White alone"],
        ["Generation X + Boomer + Silent", "Millenials + Gen Z"],
        ["High school diploma or less", "College Degree"],
        ["Below Poverty Line", "Above Poverty Line"],
        ["Not a U.S. citizen", "U.S. citizen"],
        ["Below Median House Price", "Above Median House Price"]
    ]

    # Calculate Population Density
    header = np.concatenate([header, ['Population Density']])
    pops = np.asarray([pdict[str(int(data[idx, np.argwhere(header=='Census Tract')[0, 0]]))] for idx in range(data.shape[0])]).reshape((-1, 1)).astype(np.float64)
    areas = np.asarray([adict[str(int(data[idx, np.argwhere(header=='Census Tract')[0, 0]]))] for idx in range(data.shape[0])]).reshape((-1, 1)).astype(np.float64)
    pops /= areas
    data = np.concatenate([data, pops], axis=1)

    # Scale pickup and dropoff count by area in census tract
    ctidx = np.argwhere(header=="Census Tract")[0, 0]
    pidx = np.argwhere(header=="Pickup Count")[0, 0]
    didx = np.argwhere(header=="Dropoff Count")[0, 0]
    for aridx in range(data.shape[0]):
        tract = str(int(data[aridx, ctidx]))
        area = adict[tract]
        data[aridx, pidx] /= area
        data[aridx, didx] /= area

    # Calculate demographic ratios from raw counts
    for pair in colpairs:
        c1, c2 = pair
        c1idx = np.argwhere(header==c1)[0, 0]
        c2idx = np.argwhere(header==c2)[0, 0]
        data[np.argwhere(data[:, c1idx] < 0), c1idx] = 0
        data[np.argwhere(data[:, c2idx] < 0), c2idx] = 0

        # Total population for each census tract
        rtotal = data[:, c1idx] + data[:, c2idx]

        # Percentage of population of each census tract
        for ridx in range(data.shape[0]):
            if rtotal[ridx] != 0:
                data[ridx, c1idx] /= rtotal[ridx]
                data[ridx, c2idx] /= rtotal[ridx]

            else:
                data[ridx, c1idx] = 0
                data[ridx, c2idx] = 0

    added_header = []
    added_cols = []
    for pair in colpairs:
        keep = pair[0]
        kidx = np.argwhere(header==keep)[0, 0]
        col = data[:, kidx].reshape((-1, 1))
        added_header.append('%s Percentage' % keep)
        added_cols.append(col)

    header = np.concatenate([header, added_header])
    added_cols = np.hstack(added_cols)
    data = np.concatenate([data, added_cols], axis=1)

    for pair in colpairs:
        c1, c2 = pair

        c1idx = np.argwhere(header==c1)[0, 0]
        dargs = np.delete(np.arange(header.shape[0]), c1idx)
        header = header[dargs]
        data = data[:, dargs]

        c2idx = np.argwhere(header==c2)[0, 0]
        dargs = np.delete(np.arange(header.shape[0]), c2idx)
        header = header[dargs]
        data = data[:, dargs]

    cols = [
        "Pickup Count", "Dropoff Count", 
        "Non-White Percentage", "Generation X + Boomer + Silent Percentage", 
        "High school diploma or less Percentage", "Below Poverty Line Percentage", 
        "Not a U.S. citizen Percentage", "Below Median House Price Percentage", 
    ]

    spercs = set([
        "Non-White Percentage", "Generation X + Boomer + Silent Percentage",
        "High school diploma or less Percentage", "Below Poverty Line Percentage", 
        "Not a U.S. citizen Percentage", "Below Median House Price Percentage"
    ])

    cidxs = np.asarray([np.argwhere(header==col)[0, 0] for col in cols if col in header])
    tidx = np.argwhere(header==target)[0, 0]

    cargs = np.argsort(data[:, np.argwhere(header=='Census Tract')[0, 0]])
    data = data[cargs]

    wmeans, slopes = [], []
    std = np.std(data[:, tidx])
    for cidx in cidxs:
        cargs = np.argsort(data[:, cidx])
        data = data[cargs]

        eslist, var_ds = [], []
        for ridx in range(1, data.shape[0]-1):
            nrval = np.mean(data[ridx:, tidx])
            rval = np.mean(data[:ridx, tidx])
            d = (rval - nrval) / std
            eslist.append(d)

            n1, n2 = ridx, data.shape[0]-ridx

            var_d = (
                (
                    ( (n1 + n2) / (n1 * n2) ) +
                    ( (d**2) / (2 * (n1 + n2 - 2)) )
                ) * (
                    (n1 + n2) / (n1 + n2 - 2)
                )
            )

            var_ds.append(var_d)

        eslist = np.asarray(eslist)
        var_ds = np.asarray(var_ds)
        var_all = np.var(eslist)
        var = var_ds + var_all

        slope, intercept, r_value, p_value, std_err = linregress(
            np.arange(len(eslist)),
            eslist
        )
        slope = '+' if slope >= 0 else '-'

        wmean = np.sum(eslist * (var)) / np.sum(var)
        wmeans.append(wmean)
        slopes.append(slope)

        cargs = np.argsort(data[:, np.argwhere(header=='Census Tract')[0, 0]])
        data = data[cargs]

    scores = {}
    for idx in range(len(cidxs)):
        scores[header[cidxs[idx]]] = np.abs(wmeans[idx])

    return scores


def calc_iesbs_unordered(data, header, target, pickup=False):

    tracts = json.load(open(TRACTS, 'r'))
    pdict = { tract: tracts[tract]['properties']['population'] for tract in tracts }
    adict = { tract: tracts[tract]['properties']['aland'] for tract in tracts }

    # Remove rows with any NaN values
    nanrows = np.asarray([idx for idx in range(data.shape[0]) if np.isnan(data[idx, :]).any()])
    if nanrows.shape[0] > 0: data = np.delete(data, nanrows, axis=0)

    zrows = np.argwhere(data[:, np.argwhere(header == target)[0, 0]] == 0).flatten()
    data = np.delete(data, zrows, axis=0)

    colpairs = [
        ["Non-White", "White alone"],
        ["Generation X + Boomer + Silent", "Millenials + Gen Z"],
        ["High school diploma or less", "College Degree"],
        ["Below Poverty Line", "Above Poverty Line"],
        ["Not a U.S. citizen", "U.S. citizen"],
        ["Below Median House Price", "Above Median House Price"]
    ]

    # Calculate Population Density
    header = np.concatenate([header, ['Population Density']])
    pops = np.asarray([pdict[str(int(data[idx, np.argwhere(header=='Census Tract')[0, 0]]))] for idx in range(data.shape[0])]).reshape((-1, 1)).astype(np.float64)
    areas = np.asarray([adict[str(int(data[idx, np.argwhere(header=='Census Tract')[0, 0]]))] for idx in range(data.shape[0])]).reshape((-1, 1)).astype(np.float64)
    pops /= areas
    data = np.concatenate([data, pops], axis=1)

    # Scale pickup and dropoff count by area in census tract
    ctidx = np.argwhere(header=="Census Tract")[0, 0]
    pidx = np.argwhere(header=="Pickup Count")[0, 0]
    didx = np.argwhere(header=="Dropoff Count")[0, 0]
    for aridx in range(data.shape[0]):
        tract = str(int(data[aridx, ctidx]))
        area = adict[tract]
        data[aridx, pidx] /= area
        data[aridx, didx] /= area

    # Calculate demographic ratios from raw counts
    for pair in colpairs:
        c1, c2 = pair
        c1idx = np.argwhere(header==c1)[0, 0]
        c2idx = np.argwhere(header==c2)[0, 0]
        data[np.argwhere(data[:, c1idx] < 0), c1idx] = 0
        data[np.argwhere(data[:, c2idx] < 0), c2idx] = 0

        # Total population for each census tract
        rtotal = data[:, c1idx] + data[:, c2idx]

        # Percentage of population of each census tract
        for ridx in range(data.shape[0]):
            if rtotal[ridx] != 0:
                data[ridx, c1idx] /= rtotal[ridx]
                data[ridx, c2idx] /= rtotal[ridx]

            else:
                data[ridx, c1idx] = 0
                data[ridx, c2idx] = 0

    added_header = []
    added_cols = []
    for pair in colpairs:
        keep = pair[0]
        kidx = np.argwhere(header==keep)[0, 0]
        col = data[:, kidx].reshape((-1, 1))
        added_header.append('%s Percentage' % keep)
        added_cols.append(col)

    header = np.concatenate([header, added_header])
    added_cols = np.hstack(added_cols)
    data = np.concatenate([data, added_cols], axis=1)

    for pair in colpairs:
        c1, c2 = pair

        c1idx = np.argwhere(header==c1)[0, 0]
        dargs = np.delete(np.arange(header.shape[0]), c1idx)
        header = header[dargs]
        data = data[:, dargs]

        c2idx = np.argwhere(header==c2)[0, 0]
        dargs = np.delete(np.arange(header.shape[0]), c2idx)
        header = header[dargs]
        data = data[:, dargs]

    cols = [
        "Pickup Count", "Dropoff Count", 
        "Non-White Percentage", "Generation X + Boomer + Silent Percentage", 
        "High school diploma or less Percentage", "Below Poverty Line Percentage", 
        "Not a U.S. citizen Percentage", "Below Median House Price Percentage", 
    ]

    spercs = set([
        "Non-White Percentage", "Generation X + Boomer + Silent Percentage",
        "High school diploma or less Percentage", "Below Poverty Line Percentage", 
        "Not a U.S. citizen Percentage", "Below Median House Price Percentage"
    ])

    cidxs = np.asarray([np.argwhere(header==col)[0, 0] for col in cols if col in header])
    tidx = np.argwhere(header==target)[0, 0]

    cargs = np.argsort(data[:, np.argwhere(header=='Census Tract')[0, 0]])
    data = data[cargs]

    wmeans, slopes = [], []
    for cidx in cidxs:
        cargs = np.random.permutation(data.shape[0])
        data = data[cargs]

        eslist, var_ds = [], []
        std = np.std(data[:, tidx])
        for ridx in range(1, data.shape[0]-1):
            nrval = np.mean(data[ridx:, tidx])
            rval = np.mean(data[:ridx, tidx])
            d = (rval - nrval) / std
            eslist.append(d)

            n1, n2 = ridx, data.shape[0]-ridx

            var_d = (
                (
                    ( (n1 + n2) / (n1 * n2) ) +
                    ( (d**2) / (2 * (n1 + n2 - 2)) )
                ) * (
                    (n1 + n2) / (n1 + n2 - 2)
                )
            )
            var_ds.append(var_d)

        eslist = np.asarray(eslist)
        var_ds = np.asarray(var_ds)
        var_all = np.var(eslist)
        var = var_ds + var_all

        slope, intercept, r_value, p_value, std_err = linregress(
            np.arange(len(eslist)),
            eslist
        )
        slope = '+' if slope >= 0 else '-'

        wmean = np.sum(eslist * (var)) / np.sum(var)
        wmeans.append(wmean)
        slopes.append(slope)

        cargs = np.argsort(data[:, np.argwhere(header=='Census Tract')[0, 0]])
        data = data[cargs]

    scores = {}
    for idx in range(len(cidxs)):
        scores[header[cidxs[idx]]] = np.abs(wmeans[idx])

    return scores


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inpath', type=str, required=True)
    parser.add_argument('-o', '--outpath', type=str, required=True)
    parser.add_argument('-p', '--permutations', type=int, required=True)
    parser.add_argument('-s', '--size', type=int, required=True)
    parser.add_argument('-c', '--pickup', default=False, action='store_true')
    parser.add_argument('-t', '--time', default=False, action='store_true')
    parser.add_argument('-tr', '--traffic', default=False, action='store_true')
    parser.add_argument('-cr', '--crashes', default=False, action='store_true')
    parser.add_argument('-crtr', '--traffic_and_crashes', default=False, action='store_true')
    parser.add_argument('-jb', '--jobs', default=False, action='store_true')
    parser.add_argument('-pmr', '--pickup_mrush', default=False, action='store_true')
    parser.add_argument('-per', '--pickup_erush', default=False, action='store_true')
    parser.add_argument('-dmr', '--dropoff_mrush', default=False, action='store_true')
    parser.add_argument('-der', '--dropoff_erush', default=False, action='store_true')
    parser.add_argument('-ttr', '--train', default=False, action='store_true')
    parser.add_argument('-tbs', '--bus', default=False, action='store_true')
    parser.add_argument('-ebiz', '--businesses', default=False, action='store_true')
    parser.add_argument('-ecrm', '--crimes', default=False, action='store_true')
    parser.add_argument('-egrc', '--groceries', default=False, action='store_true')
    parser.add_argument('-ehsg', '--housing', default=False, action='store_true')
    parser.add_argument('-ephl', '--potholes', default=False, action='store_true')
    args = parser.parse_args()
    inpath, outpath, perms, size, pickup, time = args.inpath, args.outpath, args.permutations, args.size, args.pickup, args.time
    traffic, crashes, traffic_and_crashes, jobs = args.traffic, args.crashes, args.traffic_and_crashes, args.jobs
    pmr, per, dmr, der = args.pickup_mrush, args.pickup_erush, args.dropoff_mrush, args.dropoff_erush
    ttr, tbs = args.train, args.bus
    businesses = args.businesses
    crimes = args.crimes
    groceries = args.groceries
    housing = args.housing
    potholes = args.potholes 

    header = np.loadtxt(inpath, delimiter=',', dtype=str, max_rows=1)
    data = np.loadtxt(inpath, delimiter=',', skiprows=1)

    if pickup: targets = ['Pickup Count', 'Dropoff Count']
    elif time: targets = ['Pickup Sec/Mi', 'Dropoff Sec/Mi']
    elif traffic: targets = ['Traffic'] 
    elif crashes: targets = ['Crashes'] 
    elif traffic_and_crashes: targets = ['Crash_vs_Traffic'] 
    elif jobs: targets = ['Art_Food_Jobs'] 
    elif pmr: targets = ['Pickup_MRush']
    elif per: targets = ['Pickup_ERush']
    elif dmr: targets = ['Dropoff_MRush']
    elif der: targets = ['Dropoff_ERush']
    elif ttr: targets = ['Trains']
    elif tbs: targets = ['Buses']
    elif businesses: targets = ['Businesses']
    elif crimes: targets = ['Crimes']
    elif groceries: targets = ['Groceries']
    elif housing: targets = ['Housing']
    elif potholes: targets = ['Potholes']
    else: targets = ['Pickup Fare/Mi', 'Dropoff Fare/Mi']

    aprobs = {}
    for target in targets:
        control = calc_iesbs(data, header, target, pickup=pickup)
        probs = { dem: 0 for dem in control }

        for i in trange(perms):
            pargs = np.random.choice(data.shape[0], size)
            perm = data[pargs]

            scores = calc_iesbs_unordered(perm, header, target, pickup=pickup)
            for dem in probs:
                if scores[dem] > control[dem]:
                    probs[dem] += 1

        for dem in probs:
            probs[dem] /= perms

        aprobs[target] = probs

    json.dump(aprobs, open(outpath, 'w'), indent=2)

if __name__ == '__main__':
    main()
