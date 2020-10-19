import json, csv

from tqdm import trange, tqdm
import numpy as np


TRAIN = '../../Data/train.csv'
BUS = '../../Data/bus.csv'


def main():

    # Train counts
    header = np.loadtxt(TRAIN, max_rows=1, delimiter=',', dtype=np.str)
    reader = csv.reader(open(TRAIN, 'r'), delimiter=',')
    data = np.asarray([line for line in reader][1:])

    tracts = {}
    for row in tqdm(data):
        tract = row[-1]
        if tract in tracts: tracts[tract] += 1
        else: tracts[tract] = 1

    json.dump(tracts, open('../data/tract_train_count.json', 'w'), indent=2)
     
    # Bus counts
    header = np.loadtxt(BUS, max_rows=1, delimiter=',', dtype=np.str)
    reader = csv.reader(open(BUS, 'r'), delimiter=',')
    data = np.asarray([line for line in reader][1:])

    tracts = {}
    for row in tqdm(data):
        tract = row[-1]
        if tract in tracts: tracts[tract] += 1
        else: tracts[tract] = 1

    json.dump(tracts, open('../data/tract_bus_count.json', 'w'), indent=2)

if __name__ == '__main__':
    main()
