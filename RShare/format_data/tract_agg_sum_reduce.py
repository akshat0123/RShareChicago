import argparse, json

from tqdm import trange, tqdm
import numpy as np


TABLEDATA = "../data/acs/table_codes_trimmed_binary.json"


ADDCOLS = np.asarray([
    'Pickup Count', 'Dropoff Count', 'Pickup Fare/Mi', 'Pickup Fare/Sec',
    'Dropoff Fare/Mi', 'Dropoff Fare/Sec' 
    # 'Pickup_MRush', 'Pickup_ERush', 'Dropoff_MRush', 'Dropoff_ERush'
])


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, nargs='*')
    parser.add_argument('-o', '--output', type=str, required=True)
    args = parser.parse_args()
    inpaths, outpath, = args.input, args.output

    tracts = {}
    for idx in trange(len(inpaths)):
        inpath = inpaths[idx]
        header = np.loadtxt(inpath, delimiter=',', max_rows=1, dtype=np.str)
        data = np.loadtxt(inpath, delimiter=',', skiprows=1)

        addidxs = np.asarray([np.argwhere(header==col)[0, 0] for col in ADDCOLS])
        cidx = np.argwhere(header=='Census Tract')[0, 0]

        for row in tqdm(data):
            ctract = row[cidx]
            if ctract in tracts: tracts[ctract][addidxs] += row[addidxs]
            else: tracts[ctract] = row

    data = np.asarray([tracts[ctract] for ctract in tracts])

    pcidx = np.argwhere(header=='Pickup Count')[0, 0]
    dcidx = np.argwhere(header=='Dropoff Count')[0, 0]
    pfmidx = np.argwhere(header=='Pickup Fare/Mi')[0, 0]
    pfsidx = np.argwhere(header=='Pickup Fare/Sec')[0, 0]
    dfmidx = np.argwhere(header=='Dropoff Fare/Mi' )[0, 0]
    dfsidx = np.argwhere(header=='Dropoff Fare/Sec')[0, 0]

    data[:, pfmidx] = np.nan_to_num(np.divide(data[:, pfmidx], data[:, pcidx]))
    data[:, pfsidx] = np.nan_to_num(np.divide(data[:, pfsidx], data[:, pcidx]))
    data[:, dfmidx] = np.nan_to_num(np.divide(data[:, dfmidx], data[:, dcidx]))
    data[:, dfsidx] = np.nan_to_num(np.divide(data[:, dfsidx], data[:, dcidx]))

    np.savetxt(outpath, data, delimiter=',', fmt='%0.8f', header=','.join(header), comments='') 


if __name__ == "__main__":
    main()
