import json, os

import matplotlib.pyplot as plt
from tqdm import trange, tqdm
import numpy as np


DATAPATH = '../../RShare/data/trips/final/'
TRACTS = '../../Data/tract_geo_data.json'


def main():
 
    tracts = json.load(open(TRACTS, 'r'))
    pdict = { tract: tracts[tract]['properties']['population'] for tract in tracts }
    adict = { tract: tracts[tract]['properties']['aland'] for tract in tracts }

    paths = sorted(['%s%s' % (DATAPATH, path) for path in os.listdir(DATAPATH) if path.startswith('201')])

    wtracts, nwtracts = {}, {}
    for path in tqdm(paths):
        header = np.loadtxt(path, delimiter=',', max_rows=1, dtype=np.str)
        data = np.loadtxt(path, delimiter=',', skiprows=1)

        ctidx = np.argwhere(header=='Census Tract')[0, 0]
        tpidx = np.argwhere(header=='Dropoff Fare/Mi')[0, 0]
        tcidx = np.argwhere(header=='Dropoff Count')[0, 0]
        nidx = np.argwhere(header=='Non-White')[0, 0]
        widx = np.argwhere(header=='White alone')[0, 0]

        header = np.concatenate([header, ['Total', 'Non-white %']])
        total = (data[:, nidx] + data[:, widx]).reshape((-1, 1))
        data = np.concatenate([data, total], axis=1)

        zargs = np.argwhere(data[:, -1]!=0).flatten()
        data = data[zargs]

        perc = (data[:, nidx] / data[:, -1]).reshape((-1, 1))
        data = np.concatenate([data, perc], axis=1)

        for row in data:
            tract = str(int(row[ctidx]))
            avg_fare_mi = row[tpidx]
            drop_count = row[tcidx]

            if row[-1] <= 0.2:

                if tract in wtracts:
                    wtracts[tract]['fare'].append(avg_fare_mi)
                    wtracts[tract]['count'].append(drop_count)

                else:
                    wtracts[tract] = {
                        'fare': [avg_fare_mi],
                        'count': [drop_count]
                    }

            else:

                if tract in nwtracts:
                    nwtracts[tract]['fare'].append(avg_fare_mi)
                    nwtracts[tract]['count'].append(drop_count)

                else:
                    nwtracts[tract] = {
                        'fare': [avg_fare_mi],
                        'count': [drop_count]
                    }

    wfares, wcounts = [], []
    for tract in wtracts:
        frow = [int(tract)]
        frow += wtracts[tract]['fare']
        if len(frow) == 12: wfares.append(frow)

        crow = [int(tract)]
        crow += wtracts[tract]['count']

        for idx in range(1, len(crow)): 
            crow[idx] /= adict[tract]

        if len(crow) == 12: 
            wcounts.append(crow)

    wfares = np.asarray(wfares)
    wcounts = np.asarray(wcounts)

    wfares = wfares[:, 1:]
    wcounts = wcounts[:, 1:]

    wfares = np.mean(wfares, axis=0)
    wcounts = np.mean(wcounts, axis=0)

    nwfares, nwcounts = [], []
    for tract in nwtracts:
       frow = [int(tract)]
       frow += nwtracts[tract]['fare']
       if len(frow) == 12: nwfares.append(frow)

       crow = [int(tract)]
       crow += nwtracts[tract]['count']

       for idx in range(1, len(crow)): 
        crow[idx] /= adict[tract]

       if len(crow) == 12: nwcounts.append(crow)

    nwfares = np.asarray(nwfares)
    nwcounts = np.asarray(nwcounts)

    nwfares = nwfares[:, 1:]
    nwcounts = nwcounts[:, 1:]

    nwfares = np.mean(nwfares, axis=0)
    nwcounts = np.mean(nwcounts, axis=0)

    fig, axarr = plt.subplots(2, 1, figsize=(10, 10))
    axarr[0].plot(wfares)
    axarr[0].plot(nwfares)
    axarr[1].plot(wcounts)
    axarr[1].plot(nwcounts)
    plt.show()


if __name__ == '__main__':
    main()
