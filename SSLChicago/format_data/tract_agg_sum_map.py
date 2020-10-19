import argparse, json

from tqdm import trange, tqdm
import numpy as np


INPATH = '../data/Strategic_Subject_List_preprocessed.csv'
OUTPATH = '../data/Strategic_Subject_List_tract_agg.csv'
TABLEDATA = "../data/table_codes_binary.json"


def main():

    with open(TABLEDATA, 'r') as infile: tdata = json.load(infile)

    header = np.loadtxt(INPATH, delimiter=',', max_rows=1, dtype=np.str)
    data = np.loadtxt(INPATH, delimiter=',', skiprows=1)

    avg_cols = [ 
        "SSL SCORE", "PREDICTOR RAT AGE AT LATEST ARREST", "PREDICTOR RAT VICTIM SHOOTING INCIDENTS", 
        "PREDICTOR RAT VICTIM BATTERY OR ASSAULT", "PREDICTOR RAT ARRESTS VIOLENT OFFENSES", 
        "PREDICTOR RAT GANG AFFILIATION", "PREDICTOR RAT NARCOTIC ARRESTS",
        "PREDICTOR RAT TREND IN CRIMINAL ACTIVITY", "PREDICTOR RAT UUW ARRESTS",
        "AGE GROUP" 
    ]

    navg_cols = [ 
        "White alone", "Not a U.S. citizen", "Millenials + Gen Z", "Generation X + Boomer + Silent", 
        "Non-White", "U.S. citizen", "High school diploma or less", "College Degree", 
        "Below Poverty Line", "Above Poverty Line", "Below Median House Price", "Above Median House Price"
    ]

    avg_args = np.asarray([np.argwhere(header == item)[0, 0] for item in header if item in avg_cols])
    navg_args = np.asarray([np.argwhere(header == item)[0, 0] for item in header if item in navg_cols])
    t_idx = np.argwhere(header=='CENSUS TRACT')[0, 0]

    # Aggregate data by tract
    tnavg_rows, tavg_rows, tcounts = {}, {}, {}
    for idx in trange(data.shape[0]):
        tract = data[idx, t_idx]    
        avg_row = data[idx, avg_args]
        navg_row = data[idx, navg_args]

        if tract in tavg_rows:
            tavg_rows[tract] += avg_row
            tcounts[tract] += 1

        else:
            tnavg_rows[tract] = navg_row
            tavg_rows[tract] = avg_row
            tcounts[tract] = 1

    # Calculate averages by tract
    for tract in tavg_rows: tavg_rows[tract] /= tcounts[tract]

    tracts = list(tavg_rows.keys())
    header = np.concatenate([['CENSUS TRACT'], avg_cols, navg_cols, ['CASE COUNT']])

    data = []
    for tract in tracts:
        row = np.concatenate([[tract], tavg_rows[tract], tnavg_rows[tract], [tcounts[tract]]])
        data.append(row)

    data = np.asarray(data).astype(np.float64)
    np.savetxt(OUTPATH, data, delimiter=',', fmt='%0.8f', header=','.join(header), comments='') 


if __name__ == "__main__":
    main()
