import argparse, json

from scipy.stats import linregress
from tqdm import trange, tqdm
import numpy as np


TRACTS = '../../Data/tract_geo_data.json'


def iesb(ndata, cidx, tidx):

    cargs = np.argsort(ndata[:, cidx])
    ndata = ndata[cargs]

    std = np.std(ndata[:, tidx])
    eslist, var_ds = [], []
    for ridx in range(1, ndata.shape[0]-1):
        nrval = np.mean(ndata[ridx:, tidx])
        rval = np.mean(ndata[:ridx, tidx])
        d = (rval - nrval) / std
        eslist.append(d)

        n1, n2 = ridx, ndata.shape[0]-ridx

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

    return wmean, slope


def main():

    tracts = json.load(open(TRACTS, 'r'))
    pdict = { tract: tracts[tract]['properties']['population'] for tract in tracts }
    adict = { tract: tracts[tract]['properties']['aland'] for tract in tracts }

    # parser = argparse.ArgumentParser()
    # parser.add_argument('-i', '--input', type=str, required=True)
    # parser.add_argument('-o', '--output', type=str, required=True)
    # parser.add_argument('-b', '--biastype', type=str, required=True)
    # parser.add_argument('-t', '--targetcol', type=str, required=True)
    # args = parser.parse_args()
    # inpath, outpath, biastype, targetcol = args.input, args.output, args.biastype, args.targetcol
    inpath = '../../RShare/data/trips/final/trips_agg_mean.csv'
    targetcol = 'Non-White Percentage'
    biastype = 'Dropoff Fare/Mi'
    outpath = '../data/diffs.json'

    header = np.loadtxt(inpath, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(inpath, delimiter=',', skiprows=1)

    # Remove rows with any NaN values
    nanrows = np.asarray([idx for idx in range(data.shape[0]) if np.isnan(data[idx, :]).any()])
    if nanrows.shape[0] > 0: data = np.delete(data, nanrows, axis=0)

    zrows = np.argwhere(data[:, np.argwhere(header == biastype)[0, 0]] == 0).flatten()
    data = np.delete(data, zrows, axis=0)

    header = np.concatenate([header, ['Population Density']])
    pops = np.asarray([pdict[str(int(data[idx, np.argwhere(header=='Census Tract')[0, 0]]))] for idx in range(data.shape[0])]).reshape((-1, 1)).astype(np.float64)
    areas = np.asarray([adict[str(int(data[idx, np.argwhere(header=='Census Tract')[0, 0]]))] for idx in range(data.shape[0])]).reshape((-1, 1)).astype(np.float64)
    pops /= areas
    data = np.concatenate([data, pops], axis=1)

    colpairs = [
        ["Non-White", "White alone"],
        ["Generation X + Boomer + Silent", "Millenials + Gen Z"],
        ["High school diploma or less", "College Degree"],
        ["Below Poverty Line", "Above Poverty Line"],
        ["Not a U.S. citizen", "U.S. citizen"],
        ["Below Median House Price", "Above Median House Price"]
    ]

    for pair in colpairs:
        c1, c2 = pair
        c1idx = np.argwhere(header==c1)[0, 0]
        c2idx = np.argwhere(header==c2)[0, 0]
        data[np.argwhere(data[:, c1idx] < 0), c1idx] = 0
        data[np.argwhere(data[:, c2idx] < 0), c2idx] = 0

        # Total population
        total = np.sum(data[:, c1idx] + data[:, c2idx])

        # Total population for each census tract
        rtotal = data[:, c1idx] + data[:, c2idx]
        rtotal[rtotal==0] = 1

        # Percentage of population of each census tract
        ctotal = rtotal / total

        data[:, c1idx] /= rtotal
        data[:, c2idx] /= rtotal

    added_header = []
    added_cols = []
    for pair in colpairs:
        keep, toss = pair
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

    # Scale pickup and dropoff count by area in census tract
    ctidx = np.argwhere(header=="Census Tract")[0, 0]
    pidx = np.argwhere(header=="Pickup Count")[0, 0]
    didx = np.argwhere(header=="Dropoff Count")[0, 0]
    for aridx in range(data.shape[0]):
        tract = str(int(data[aridx, ctidx]))
        area = adict[tract]
        data[aridx, pidx] /= area
        data[aridx, didx] /= area

    cidx = np.argwhere(header==targetcol)[0, 0]
    tidx = np.argwhere(header==biastype)[0, 0]

    cargs = np.argsort(data[:, np.argwhere(header=='Census Tract')[0, 0]])
    data = data[cargs]
    owmean, oslope = iesb(data, cidx, tidx)
    
    diffs = {}
    for epoch in trange(data.shape[0]):

        tract = str(int(data[epoch, ctidx]))
        eargs = np.arange(data.shape[0])
        eargs = eargs[eargs != epoch]
        ndata = np.copy(data)[eargs]

        cargs = np.argsort(ndata[:, np.argwhere(header=='Census Tract')[0, 0]])
        ndata = ndata[cargs]
        wmean, slope = iesb(ndata, cidx, tidx)
        diff = np.abs(owmean - wmean)
        diffs[tract] = diff

    json.dump(diffs, open(outpath, 'w'), indent=2)


if __name__ == '__main__':
    main()
