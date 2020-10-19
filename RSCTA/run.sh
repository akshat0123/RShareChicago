cd src;

# Get train and bus station count by census tract
python3 get_tract_counts.py;

# Merge with other tract aggregate data
python3 merge.py

cd ..;

cd ../RShare/analysis;

# Calculate bias on train stops
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_train.csv -o ../../RSCTA/data/bias_train.csv -b "Trains"
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_train.csv -o ../../RSCTA/data/bias_train_pickup_fare.csv -b "Pickup Fare/Mi"
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_train.csv -o ../../RSCTA/data/bias_train_dropoff_fare.csv -b "Dropoff Fare/Mi"
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_train.csv -o ../../RSCTA/data/bias_train_pickup_freq.csv -b "Pickup Count"
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_train.csv -o ../../RSCTA/data/bias_train_dropoff_freq.csv -b "Dropoff Count"
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_train.csv -o ../../RSCTA/data/bias_train_pickup_time.csv -b "Pickup Sec/Mi"
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_train.csv -o ../../RSCTA/data/bias_train_dropoff_time.csv -b "Dropoff Sec/Mi"

# Calculate pvals on train stops
python3 pvals.py -i ../../RSCTA/data/tract_agg_mean_train.csv -o ../../RSCTA/data/train_trips_trian_pvals.json -p 1000 -s 100 -ttr;
python3 pvals.py -i ../../RSCTA/data/tract_agg_mean_train.csv -o ../../RSCTA/data/train_trips_price_pvals.json -p 1000 -s 100;
python3 pvals.py -i ../../RSCTA/data/tract_agg_mean_train.csv -o ../../RSCTA/data/train_trips_freq_pvals.json -p 1000 -s 100 -c;
python3 pvals.py -i ../../RSCTA/data/tract_agg_mean_train.csv -o ../../RSCTA/data/train_trips_time_pvals.json -p 1000 -s 100 -t;

# Calculate bias on bus stops
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_bus.csv -o ../../RSCTA/data/bias_bus.csv -b "Buses"
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_bus.csv -o ../../RSCTA/data/bias_bus_pickup_fare.csv -b "Pickup Fare/Mi"
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_bus.csv -o ../../RSCTA/data/bias_bus_dropoff_fare.csv -b "Dropoff Fare/Mi"
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_bus.csv -o ../../RSCTA/data/bias_bus_pickup_freq.csv -b "Pickup Count"
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_bus.csv -o ../../RSCTA/data/bias_bus_dropoff_freq.csv -b "Dropoff Count"
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_bus.csv -o ../../RSCTA/data/bias_bus_pickup_time.csv -b "Pickup Sec/Mi"
python3 bias.py -i ../../RSCTA/data/tract_agg_mean_bus.csv -o ../../RSCTA/data/bias_bus_dropoff_time.csv -b "Dropoff Sec/Mi"

# Calculate pvals on train stops
python3 pvals.py -i ../../RSCTA/data/tract_agg_mean_bus.csv -o ../../RSCTA/data/bus_trips_bus_pvals.json -p 1000 -s 100 -tbs;
python3 pvals.py -i ../../RSCTA/data/tract_agg_mean_bus.csv -o ../../RSCTA/data/bus_trips_price_pvals.json -p 1000 -s 100;
python3 pvals.py -i ../../RSCTA/data/tract_agg_mean_bus.csv -o ../../RSCTA/data/bus_trips_freq_pvals.json -p 1000 -s 100 -c;
python3 pvals.py -i ../../RSCTA/data/tract_agg_mean_bus.csv -o ../../RSCTA/data/bus_trips_time_pvals.json -p 1000 -s 100 -t;

cd ..;
