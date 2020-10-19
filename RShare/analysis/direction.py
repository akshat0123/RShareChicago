import argparse, json

from sklearn.preprocessing import StandardScaler
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
from tqdm import tqdm
import numpy as np

from utils import combine_columns, scale


TRACTS = '../../Data/tract_geo_data.json'


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-b', '--biastype', type=str, required=True)
    args = parser.parse_args()
    inpath, outpath, biastype  = args.input, args.output, args.biastype

    tracts = json.load(open(TRACTS, 'r'))
    pdict = { tract: tracts[tract]['properties']['population'] for tract in tracts }
    adict = { tract: tracts[tract]['properties']['aland'] for tract in tracts }

    header = np.loadtxt(inpath, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(inpath, delimiter=',', skiprows=1)
    
    # Remove rows with any NaN values
    nanrows = np.asarray([idx for idx in range(data.shape[0]) if np.isnan(data[idx, :]).any()])
    if nanrows.shape[0] > 0: data = np.delete(data, nanrows, axis=0)

    # Remove rows where requested bias type is 0
    zrows = np.argwhere(data[:, np.argwhere(header==biastype)[0, 0]] == 0).flatten()
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
    tidx = np.argwhere(header==biastype)[0, 0]

    eslists, xlists, titles = [], [], []
    for cidx in cidxs:
        titles.append(header[cidx])
        cargs = np.argsort(data[:, cidx])
        data = data[cargs]

        eslist, xlist, var_ds = [], [], []
        std = np.std(data[:, tidx])
        for ridx in range(1, data.shape[0]-1):
            nrval = np.mean(data[ridx:, tidx])
            rval = np.mean(data[:ridx, tidx])
            d = (rval - nrval) / std
            eslist.append(d)
            xlist.append(data[ridx, cidx])

        eslist = np.asarray(eslist)
        xlist = np.asarray(xlist)
        eslists.append(eslist)
        xlists.append(xlist)

    eslists = np.asarray(eslists)
    xlists = np.asarray(xlists)

    tnames = {
        'Pickup Count': '# of pickups', 
        'Dropoff Count': '# of dropoffs', 
        'Non-White Percentage': '% of non-white pop', 
        'Generation X + Boomer + Silent Percentage': '% of >= 40 pop', 
        'High school diploma or less Percentage': '% of highschool educated or less pop', 
        'Below Poverty Line Percentage': '% below poverty line', 
        'Not a U.S. citizen Percentage': '% non-U.S. citizens', 
        'Below Median House Price Percentage': '% living in homes < median house price'
    }

    titles = [tnames[title] for title in titles]

    fig, axarr = plt.subplots(2, 4, figsize=(15, 7))

    ridx = cidx = 0
    for eidx in range(len(eslists)):
        eslist = eslists[eidx]
        xlist = xlists[eidx]
        axarr[ridx][cidx].plot(xlist, eslist)
        axarr[ridx][cidx].set_title(titles[eidx])
        if cidx >= 3: ridx +=1; cidx = 0
        else: cidx += 1

    plt.savefig(outpath, bbox_inches='tight')


if __name__ == '__main__':
    main()
