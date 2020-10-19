# Preprocess Strategic Subject List data
cd format_data;
python3 clean.py; 
python3 merge_data.py;
python3 preprocessing.py;
python3 tract_agg_sum_map.py;
cd ..;

# Calculate bias for Strategic Subject List data
cd analysis;
python3 effect_size.py;
python3 iesb.py;
cd ..;
