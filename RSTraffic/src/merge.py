import json

from tqdm import trange, tqdm
import numpy as np


DATA = '../../RShare/data/trips/final/trips_agg_mean.csv'
CRASHES = '../data/tract_traffic_crash_count.json'
TRAFFIC = '../data/tract_traffic_count.json'
TRACTS = '../../Data/tract_geo_data.json'


def main():

    header = np.loadtxt(DATA, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(DATA, delimiter=',', skiprows=1)
    tidx = np.argwhere(header=='Census Tract')[0, 0]

    tracts = json.load(open(TRACTS, 'r'))
    pdict = { tract: tracts[tract]['properties']['population'] for tract in tracts }
    adict = { tract: tracts[tract]['properties']['aland'] for tract in tracts }

    # Traffic
    tdata = json.load(open(TRAFFIC, 'r'))
    tkeys = set(list(tdata.keys()))
    nrows = []
    for row in tqdm(data):
        if row[tidx].astype(np.int).astype(str) in tkeys: 
            trafficcount = tdata[row[tidx].astype(np.int).astype(str)]
            trafficratio = trafficcount / adict[row[tidx].astype(np.int).astype(str)]
            nrows.append(np.concatenate([row, [trafficratio]]))
        
    nrows = np.asarray(nrows)
    nheader = np.concatenate([header, ['Traffic']])
    np.savetxt('../data/tract_agg_mean_traffic.csv', nrows, delimiter=',', fmt='%0.8f', header=','.join(nheader), comments='') 

    # Crashes
    cdata = json.load(open(CRASHES, 'r'))
    ckeys = set(list(cdata.keys()))
    nrows = []
    for row in tqdm(data):
        if row[tidx].astype(np.int).astype(str) in ckeys: 
            crashcount = cdata[row[tidx].astype(np.int).astype(str)]
            crashratio = crashcount / adict[row[tidx].astype(np.int).astype(str)]
            nrows.append(np.concatenate([row, [crashratio]]))
        
    nrows = np.asarray(nrows)
    nheader = np.concatenate([header, ['Crashes']])
    np.savetxt('../data/tract_agg_mean_crash.csv', nrows, delimiter=',', fmt='%0.8f', header=','.join(nheader), comments='') 


if __name__ == '__main__':
    main()
