import json

GEO = '../data/tmap_by_area_adj.geojson'
DIFFS = '../data/diffs.json'


def main():

    diffs = json.load(open(DIFFS, 'r'))
    tmaps = json.load(open(GEO, 'r'))
    
    for tidx in range(len(tmaps['features'])):
        tdata = tmaps['features'][tidx]
        props = tdata['properties']
        tract = props['full_geoid'][-11:]

        if tract in diffs:
            tmaps['features'][tidx]['properties']['diff'] = diffs[tract]

    json.dump(tmaps, open('../data/tmap_by_area_adj_diffs.geojson', 'w'), indent=2)


if __name__ == '__main__':
    main()
