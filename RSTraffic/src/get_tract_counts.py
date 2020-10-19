import json, csv

from tqdm import trange, tqdm
import numpy as np


COUNTS = '../../Data/traffic_counts.csv'
CRASHES = '../../Data/traffic_crashes.csv'


def main():

    # Traffic Counts
    header = np.loadtxt(COUNTS, max_rows=1, delimiter=',', dtype=np.str)
    csvreader = csv.reader(open(COUNTS, 'r'), delimiter=',', quotechar='"')
    data = [line for line in csvreader][1:]

    vidx = np.argwhere(header=='total passing vehicle volume')[0, 0]

    tracts = {}
    for row in tqdm(data):
        tract = row[-1]
        vol = np.float64(row[vidx])

        if tract in tracts: tracts[tract] += vol
        else: tracts[tract] = vol

    json.dump(tracts, open('../data/tract_traffic_count.json', 'w'), indent=2)
        
    # # Traffic Crashes
    header = np.loadtxt(CRASHES, max_rows=1, delimiter=',', dtype=np.str)
    csvreader = csv.reader(open(CRASHES, 'r'), delimiter=',', quotechar='"')
    data = [line for line in csvreader][1:]

    tracts = {}
    for row in tqdm(data):
        tract = row[-1]
        if tract in tracts: tracts[tract] += 1
        else: tracts[tract] = 1 

    json.dump(tracts, open('../data/tract_traffic_crash_count.json', 'w'), indent=2)


if __name__ == '__main__':
    main()
