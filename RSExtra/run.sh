cd src;

# Get traffic and crashes by census tract
python3 get_tract_counts.py;

# Merge with other tract aggregate data
python3 merge.py

cd ..;

# Calculate bias on all extra attributes
cd ../RShare/analysis;
python3 bias.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/bias_businesses.csv -b "Businesses"
python3 bias.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/bias_crimes.csv -b "Crimes"
python3 bias.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/bias_groceries.csv -b "Groceries"
python3 bias.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/bias_housing.csv -b "Housing"
python3 bias.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/bias_potholes.csv -b "Potholes"
python3 bias.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/bias_extra_pickup_fare.csv -b "Pickup Fare/Mi"
python3 bias.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/bias_extra_dropoff_fare.csv -b "Dropoff Fare/Mi"
python3 bias.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/bias_extra_pickup_freq.csv -b "Pickup Count"
python3 bias.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/bias_extra_dropoff_freq.csv -b "Dropoff Count"
python3 bias.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/bias_extra_pickup_time.csv -b "Pickup Sec/Mi"
python3 bias.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/bias_extra_dropoff_time.csv -b "Dropoff Sec/Mi"

# Calculate pvals on all extra attributes
python3 pvals.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/extra_trips_businesses_pvals.json -p 1000 -s 100 -ebiz;
python3 pvals.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/extra_trips_crimes_pvals.json -p 1000 -s 100 -ecrm;
python3 pvals.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/extra_trips_groceries_pvals.json -p 1000 -s 100 -egrc;
python3 pvals.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/extra_trips_housing_pvals.json -p 1000 -s 100 -ehsg;
python3 pvals.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/extra_trips_potholes_pvals.json -p 1000 -s 100 -ephl;
python3 pvals.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/extra_trips_price_pvals.json -p 1000 -s 100;
python3 pvals.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/extra_trips_freq_pvals.json -p 1000 -s 100 -c;
python3 pvals.py -i ../../RSExtra/data/tract_agg_mean_extra.csv -o ../../RSExtra/data/extra_trips_time_pvals.json -p 1000 -s 100 -t;
cd ..;
