import json

from tqdm import trange, tqdm
import numpy as np


DATA = '../../RShare/data/trips/final/trips_agg_mean.csv'
TRACTS = '../../Data/tract_geo_data.json'
TRAINS = '../data/tract_train_count.json'
BUS = '../data/tract_bus_count.json'


def main():

    header = np.loadtxt(DATA, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(DATA, delimiter=',', skiprows=1)
    tidx = np.argwhere(header=='Census Tract')[0, 0]

    tracts = json.load(open(TRACTS, 'r'))
    pdict = { tract: tracts[tract]['properties']['population'] for tract in tracts }
    adict = { tract: tracts[tract]['properties']['aland'] for tract in tracts }

    # Train
    tdata = json.load(open(TRAINS, 'r'))
    tkeys = set(list(tdata.keys()))
    nrows = []
    for row in tqdm(data):
        if row[tidx].astype(np.int).astype(str) in tkeys: 
            traincounts = tdata[row[tidx].astype(np.int).astype(str)]
            trainratio = traincounts / adict[row[tidx].astype(np.int).astype(str)]
            nrows.append(np.concatenate([row, [trainratio]]))
        
    nrows = np.asarray(nrows)
    nheader = np.concatenate([header, ['Trains']])
    np.savetxt('../data/tract_agg_mean_train.csv', nrows, delimiter=',', fmt='%0.8f', header=','.join(nheader), comments='') 

    # Buses 
    bdata = json.load(open(BUS, 'r'))
    bkeys = set(list(bdata.keys()))
    nrows = []
    for row in tqdm(data):
        if row[tidx].astype(np.int).astype(str) in bkeys: 
            buscounts = bdata[row[tidx].astype(np.int).astype(str)]
            busratio = buscounts / adict[row[tidx].astype(np.int).astype(str)]
            nrows.append(np.concatenate([row, [busratio]]))
        
    nrows = np.asarray(nrows)
    nheader = np.concatenate([header, ['Buses']])
    np.savetxt('../data/tract_agg_mean_bus.csv', nrows, delimiter=',', fmt='%0.8f', header=','.join(nheader), comments='') 


if __name__ == '__main__':
    main()
