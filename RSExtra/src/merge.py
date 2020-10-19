import json, csv

from tqdm import trange, tqdm
import numpy as np


DATA = '../../RShare/data/trips/final/trips_agg_mean.csv'
BUSINESSES = '../data/businesses_counts.json'
GROCERIES = '../data/groceries_counts.json'
TRACTS = '../../Data/tract_geo_data.json'
POTHOLES = '../data/potholes_counts.json'
HOUSING = '../data/housing_counts.json'
CRIMES = '../data/crimes_counts.json'


def main():

    ipaths = [ BUSINESSES, CRIMES, GROCERIES, HOUSING, POTHOLES ]

    header = np.loadtxt(DATA, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(DATA, delimiter=',', skiprows=1)
    tidx = np.argwhere(header=='Census Tract')[0, 0]

    tracts = json.load(open(TRACTS, 'r'))
    pdict = { tract: tracts[tract]['properties']['population'] for tract in tracts }
    adict = { tract: tracts[tract]['properties']['aland'] for tract in tracts }

    for pidx in trange(len(ipaths)):
        ipath = ipaths[pidx]

        cname = ipath.split('/')[-1].split('_')[0]
        cname = [char for char in cname] 
        cname[0] = cname[0].upper()
        cname = ''.join(cname)

        header = np.concatenate([header, [cname]])
        data = np.concatenate([
            data,
            np.full((data.shape[0], 1), -1)
        ], axis=1)

        tdict = json.load(open(ipath, 'r'))
        for ridx in trange(data.shape[0]):
            tract = str(int(data[ridx, tidx]))

            if tract in tdict: 
                count = tdict[tract]
                ratio = count / adict[tract]
                data[ridx, -1] = ratio 

    np.savetxt('../data/tract_agg_mean_extra.csv', data, delimiter=',', fmt='%0.8f', header=','.join(header), comments='') 


if __name__ == '__main__':
    main()
