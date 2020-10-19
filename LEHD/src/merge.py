import json

from tqdm import trange, tqdm
import numpy as np


DATA = '../../RShare/data/trips/final/trips_agg_mean.csv'
TRACTS = '../../Data/tract_geo_data.json'
RAC = '../../Data/lehd_rac.csv'
WAC = '../../Data/lehd_wac.csv'


def main():

    tracts = json.load(open(TRACTS, 'r'))
    pdict = { tract: tracts[tract]['properties']['population'] for tract in tracts }
    adict = { tract: tracts[tract]['properties']['aland'] for tract in tracts }

    header = np.loadtxt(DATA, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(DATA, delimiter=',', skiprows=1)
    tidx = np.argwhere(header=='Census Tract')[0, 0]

    lheader = np.loadtxt(WAC, delimiter=',', max_rows=1, dtype=np.str)
    ldata = np.loadtxt(WAC, delimiter=',', skiprows=1)
    ltidx = np.argwhere(lheader=='Workplace_Census_Block_Code')[0, 0]
    leidx = np.argwhere(lheader=='Number_of_jobs_in_NAICS_sector_71_Arts_Entertainment_and_Recreation')[0, 0]
    lfidx = np.argwhere(lheader=='Number_of_jobs_in_NAICS_sector_72_Accommodation_and_Food_Services')[0, 0]
    ljidx = np.argwhere(lheader=='Total_number_of_jobs')[0, 0]

    ltracts = {}
    for row in tqdm(ldata):
        tract = row[ltidx]
        ent = row[leidx]
        food = row[lfidx]
        jobs = row[ljidx]
        ltracts[tract] = (ent + food) / adict[str(int(tract))]

    header = np.concatenate([header, ['Art_Food_Jobs']])
    nrows = []
    for row in tqdm(data):
        tract = row[tidx]
        if tract in ltracts:
            nrows.append(np.concatenate([row, [ltracts[tract]]]))

    nrows = np.asarray(nrows)
    np.savetxt('../data/tract_agg_mean_jobs_wac.csv', nrows, delimiter=',', fmt='%0.8f', header=','.join(header), comments='') 

    header = np.loadtxt(DATA, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(DATA, delimiter=',', skiprows=1)
    tidx = np.argwhere(header=='Census Tract')[0, 0]

    lheader = np.loadtxt(RAC, delimiter=',', max_rows=1, dtype=np.str)
    ldata = np.loadtxt(RAC, delimiter=',', skiprows=1)
    ltidx = np.argwhere(lheader=='Residence_Census_Block_Code')[0, 0]
    leidx = np.argwhere(lheader=='Number_of_jobs_in_NAICS_sector_71_Arts_Entertainment_and_Recreation')[0, 0]
    lfidx = np.argwhere(lheader=='Number_of_jobs_in_NAICS_sector_72_Accommodation_and_Food_Services')[0, 0]
    ljidx = np.argwhere(lheader=='Total_number_of_jobs')[0, 0]

    ltracts = {}
    for row in tqdm(ldata):
        tract = row[ltidx]
        ent = row[leidx]
        food = row[lfidx]
        jobs = row[ljidx]
        ltracts[tract] = (ent + food) / jobs

    header = np.concatenate([header, ['Art_Food_Jobs']])
    nrows = []
    for row in tqdm(data):
        tract = row[tidx]
        if tract in ltracts:
            nrows.append(np.concatenate([row, [ltracts[tract]]]))

    nrows = np.asarray(nrows)
    np.savetxt('../data/tract_agg_mean_jobs_rac.csv', nrows, delimiter=',', fmt='%0.8f', header=','.join(header), comments='') 


if __name__ == '__main__':
    main()
