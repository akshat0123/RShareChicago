import json, csv

from tqdm import trange, tqdm
import numpy as np


BUSINESSES = '../../Data/businesses.csv'
CRIMES = '../../Data/crimes.csv'
GROCERIES = '../../Data/groceries.csv'
HOUSING = '../../Data/housing.csv'
POTHOLES = '../../Data/potholes.csv'


def main():

    ipaths = [ BUSINESSES, CRIMES, GROCERIES, HOUSING, POTHOLES ]
    opaths = [
        '../data/businesses_counts.json', '../data/crimes_counts.json',
        '../data/groceries_counts.json', '../data/housing_counts.json',
        '../data/potholes_counts.json'
    ]

    for pidx in trange(len(ipaths)):
        ipath, opath = ipaths[pidx], opaths[pidx]

        header = np.loadtxt(ipath, max_rows=1, delimiter=',', dtype=np.str)
        csvreader = csv.reader(open(ipath, 'r'), delimiter=',', quotechar='"')
        data = np.asarray([line for line in csvreader][1:])

        tracts = {}
        for row in tqdm(data):
            tract = row[-1]
            
            if tract in tracts: tracts[tract] += 1
            else: tracts[tract] = 1
        
        json.dump(tracts, open(opath, 'w'), indent=2)


if __name__ == '__main__':
    main()
