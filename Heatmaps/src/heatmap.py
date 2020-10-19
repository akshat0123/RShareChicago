import json

from tqdm import trange, tqdm
import numpy as np


RSTRAFFIC = '../../RSTraffic/data/tract_agg_mean_traffic.csv'
RSCRASH = '../../RSTraffic/data/tract_agg_mean_crash.csv'
RSHARE = '../../RShare/data/trips/final/trips_agg_mean.csv'
RSCTATRAIN = '../../RSCTA/data/tract_agg_mean_train.csv'
LEHDRAC = '../../LEHD/data/tract_agg_mean_jobs_rac.csv'
LEHDWAC = '../../LEHD/data/tract_agg_mean_jobs_wac.csv'
RSCTABUS = '../../RSCTA/data/tract_agg_mean_bus.csv'
EXTRA = '../../RSExtra/data/tract_agg_mean_extra.csv'
MAP = '../../Data/tract_geo_data.json'


def main():

    paths = [ RSHARE, RSCTATRAIN, LEHDRAC, LEHDWAC, RSCTABUS, EXTRA, RSTRAFFIC, RSCRASH ]
    tmap = json.load(open(MAP, 'r'))

    pdict = { tract: tmap[tract]['properties']['population'] for tract in tmap }
    adict = { tract: tmap[tract]['properties']['aland'] for tract in tmap }

    propnames = {
        'White alone': '% White', 
        'Not a U.S. citizen': '% Non-U.S. citizen', 
        'Millenials + Gen Z': '% Younger than 40', 
        'Generation X + Boomer + Silent': '% Older than 40',
        'Non-White': '% Non-white', 
        'U.S. citizen': '% U.S. citizen', 
        'High school diploma or less': '% Highschool education or less', 
        'College Degree': '% College educated',
        'Below Poverty Line': '% Below poverty line', 
        'Above Poverty Line': '% Above poverty line', 
        'Below Median House Price': '% Living in home below median house price', 
        'Above Median House Price': '% Living in home above median house price', 
        'Pickup Count': '# of Pickups', 
        'Dropoff Count': '# of Dropoffs', 
        'Pickup_MRush': '# of pickups during morning rush', 
        'Pickup_ERush': '# of pickups during evening rush',
        'Dropoff_MRush': '# of dropoffs during morning rush', 
        'Dropoff_ERush': '# of dropoffs during evening rush', 
        'Art_Food_Jobs_WAC': '% of jobs in arts/food/entertainment', 
        'Art_Food_Jobs_RAC': '% of workers in arts/food/entertainment', 
        'Businesses': '# of businesses', 
        'Crimes': '# of crimes',
        'Groceries': '# of groceries', 
        'Housing': '# of affordable housing', 
        'Potholes': '# of potholes',
        'Trains': '# of subway stations', 
        'Buses': '# of bus stops',
        'Crashes': '# of crashes',
        'Traffic': '# of cars daily'
    }

    aheaders = set([])
    for path in paths:
        header = np.loadtxt(path, delimiter=',', max_rows=1, dtype=np.str)

        if path == LEHDRAC: header[np.argwhere(header == 'Art_Food_Jobs')[0, 0]] = 'Art_Food_Jobs_RAC'
        elif path == LEHDWAC: header[np.argwhere(header == 'Art_Food_Jobs')[0, 0]] = 'Art_Food_Jobs_WAC'

        header = np.asarray([propnames[h] if h in propnames else h for h in header])
        data = np.loadtxt(path, delimiter=',', skiprows=1)
        tidx = np.argwhere(header=='Census Tract')[0, 0]

        if path == RSHARE:
            pidx = np.argwhere(header=="# of Pickups")[0, 0]
            didx = np.argwhere(header=="# of Dropoffs")[0, 0]
            for ridx in range(data.shape[0]):
                tract = str(int(data[ridx, tidx]))
                area = adict[tract]
                data[ridx, pidx] /= area
                data[ridx, didx] /= area

        for row in tqdm(data):
            tract = str(int(row[tidx]))

            if tract in tmap:
                for cidx in range(row.shape[0]):
                    if header[cidx] not in tmap[tract]['properties']:
                        if row[cidx] != -1:
                            tmap[tract]['properties'][header[cidx]] = row[cidx]
                            aheaders.add(header[cidx])

    adjs = set([
        '% White', '% Non-U.S. citizen', '% Younger than 40', '% Older than 40', '% Non-white', 
        '% U.S. citizen', '% Highschool education or less', '% College educated', '% Below poverty line', '% Above poverty line', 
        '% Living in home below median house price', '% Living in home above median house price', 
    ])

    apairs = [
        ['% Non-white', '% White'],
        ['% Non-U.S. citizen', '% U.S. citizen'],
        ['% Older than 40', '% Younger than 40'],
        ['% Highschool education or less', '% College educated'],
        ['% Below poverty line', '% Above poverty line'],
        ['% Living in home below median house price', '% Living in home above median house price'],
    ]

    ntmap = {
        "type": "FeatureCollection",
        "features": []
    }

    tracts = list(tmap.keys())
    for tract in tracts:

        geo = tmap[tract]['geometry']
        props = tmap[tract]['properties']

        seen = set([])
        for prop in props:
            if prop in adjs:
                for pair in apairs:
                    if prop in pair:

                        if prop not in seen:
                            pairtotal = (props[pair[0]] + props[pair[1]])

                            if pairtotal > 0:
                                props[pair[0]] /= pairtotal
                                props[pair[1]] /= pairtotal 
                                
                            else:
                                props[pair[0]] = 0
                                props[pair[1]] = 0 

                            seen.add(pair[0])
                            seen.add(pair[1])

        if props['aland']: props['Population Density'] = props['population'] / props['aland']
        else: props['Population Density'] = 0

        entry = {
            "type": "Feature",
            "geometry": geo,
            "properties": props
        }

        ntmap["features"].append(entry)

    json.dump(ntmap, open('../data/tmap.geojson', 'w'), indent=4)


if __name__ == '__main__':
    main()
