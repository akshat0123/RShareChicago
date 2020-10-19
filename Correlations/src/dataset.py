import json

from tqdm import trange, tqdm
import numpy as np


INPATH = '../../Heatmaps/data/tmap_by_area_adj_diffs.geojson'
OUTPATH = '../data/data.csv'

COLS = [
    'Census Tract', 'Pickup Fare/Mi', 'Dropoff Fare/Mi', 'Pickup Fare/Sec', 'Dropoff Fare/Sec', 'Pickup Sec/Mi', 'Dropoff Sec/Mi',
    '# of Dropoffs', '# of Pickups', '# of affordable housing', '# of bus stops', '# of businesses', '# of cars daily',
    '# of crashes', '# of crimes', '# of dropoffs during evening rush', '# of dropoffs during morning rush', '# of groceries', 
    '# of pickups during evening rush', '# of pickups during morning rush', '# of potholes', '# of subway stations', '% Above poverty line', 
    '% Below poverty line', '% College educated', '% Highschool education or less', '% Living in home above median house price', 
    '% Living in home below median house price', '% Non-U.S. citizen', '% Non-white', '% Older than 40', '% U.S. citizen',
    '% White', '% Younger than 40', '% of jobs in arts/food/entertainment', '% of workers in arts/food/entertainment',
    'Population Density', 'diff', 'aland'
]

def main():

    tmap = json.load(open(INPATH, 'r'))['features']

    header = np.asarray(COLS)
    data = []

    for tract in tqdm(tmap):
        props = tract['properties']
        row = []

        for col in header:
            if col in props: row.append(props[col])
            else: row.append(-1)

        data.append(row)

    data = np.asarray(data)
    np.savetxt(OUTPATH, data, delimiter=',', fmt='%0.8f', header=','.join(header), comments='') 


if __name__ == '__main__':
    main()
