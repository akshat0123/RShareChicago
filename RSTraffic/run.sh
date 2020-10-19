cd src;

# Get traffic and crashes by census tract
python3 get_tract_counts.py;

# Merge with other tract aggregate data
python3 merge.py

cd ..;

# Calculate bias on traffic
cd ../RShare/analysis;
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_traffic.csv -o ../../RSTraffic/data/bias_traffic.csv -b "Traffic"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_traffic.csv -o ../../RSTraffic/data/bias_traffic_pickup_fare.csv -b "Pickup Fare/Mi"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_traffic.csv -o ../../RSTraffic/data/bias_traffic_dropoff_fare.csv -b "Dropoff Fare/Mi"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_traffic.csv -o ../../RSTraffic/data/bias_traffic_pickup_freq.csv -b "Pickup Count"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_traffic.csv -o ../../RSTraffic/data/bias_traffic_dropoff_freq.csv -b "Dropoff Count"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_traffic.csv -o ../../RSTraffic/data/bias_traffic_pickup_time.csv -b "Pickup Sec/Mi"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_traffic.csv -o ../../RSTraffic/data/bias_traffic_dropoff_time.csv -b "Dropoff Sec/Mi"

# Calculate pvals on traffic
python3 pvals.py -i ../../RSTraffic/data/tract_agg_mean_traffic.csv -o ../../RSTraffic/data/traffic_trips_traffic_pvals.json -p 1000 -s 100 -tr;
python3 pvals.py -i ../../RSTraffic/data/tract_agg_mean_traffic.csv -o ../../RSTraffic/data/traffic_trips_price_pvals.json -p 1000 -s 100;
python3 pvals.py -i ../../RSTraffic/data/tract_agg_mean_traffic.csv -o ../../RSTraffic/data/traffic_trips_freq_pvals.json -p 1000 -s 100 -c;
python3 pvals.py -i ../../RSTraffic/data/tract_agg_mean_traffic.csv -o ../../RSTraffic/data/traffic_trips_time_pvals.json -p 1000 -s 100 -t;

# Calculate bias on crashes
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash.csv -o ../../RSTraffic/data/bias_crashes.csv -b "Crashes"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash.csv -o ../../RSTraffic/data/bias_crashes_pickup_fare.csv -b "Pickup Fare/Mi"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash.csv -o ../../RSTraffic/data/bias_crashes_dropoff_fare.csv -b "Dropoff Fare/Mi"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash.csv -o ../../RSTraffic/data/bias_crashes_pickup_freq.csv -b "Pickup Count"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash.csv -o ../../RSTraffic/data/bias_crashes_dropoff_freq.csv -b "Dropoff Count"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash.csv -o ../../RSTraffic/data/bias_crashes_pickup_time.csv -b "Pickup Sec/Mi"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash.csv -o ../../RSTraffic/data/bias_crashes_dropoff_time.csv -b "Dropoff Sec/Mi"

# Calculate pvals on crashes
python3 pvals.py -i ../../RSTraffic/data/tract_agg_mean_crash.csv -o ../../RSTraffic/data/crashes_trips_crashes_pvals.json -p 1000 -s 100 -cr;
python3 pvals.py -i ../../RSTraffic/data/tract_agg_mean_crash.csv -o ../../RSTraffic/data/crashes_trips_price_pvals.json -p 1000 -s 100;
python3 pvals.py -i ../../RSTraffic/data/tract_agg_mean_crash.csv -o ../../RSTraffic/data/crashes_trips_freq_pvals.json -p 1000 -s 100 -c;
python3 pvals.py -i ../../RSTraffic/data/tract_agg_mean_crash.csv -o ../../RSTraffic/data/crashes_trips_time_pvals.json -p 1000 -s 100 -t;

# Calculate bias on crashes vs traffic
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash_vs_traffic.csv -o ../../RSTraffic/data/bias_crashes_vs_traffic.csv -b "Crash_vs_Traffic"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash_vs_traffic.csv -o ../../RSTraffic/data/bias_crashes_vs_traffic_pickup_fare.csv -b "Pickup Fare/Mi"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash_vs_traffic.csv -o ../../RSTraffic/data/bias_crashes_vs_traffic_dropoff_fare.csv -b "Dropoff Fare/Mi"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash_vs_traffic.csv -o ../../RSTraffic/data/bias_crashes_vs_traffic_pickup_freq.csv -b "Pickup Count"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash_vs_traffic.csv -o ../../RSTraffic/data/bias_crashes_vs_traffic_dropoff_freq.csv -b "Dropoff Count"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash_vs_traffic.csv -o ../../RSTraffic/data/bias_crashes_vs_traffic_pickup_time.csv -b "Pickup Sec/Mi"
python3 bias.py -i ../../RSTraffic/data/tract_agg_mean_crash_vs_traffic.csv -o ../../RSTraffic/data/bias_crashes_vs_traffic_dropoff_time.csv -b "Dropoff Sec/Mi"

# Calculate pvals on crashes vs traffic
python3 pvals.py -i ../../RSTraffic/data/tract_agg_mean_crash_vs_traffic.csv -o ../../RSTraffic/data/crashes_vs_traffic_trips_crashes_vs_traffic_pvals.json -p 1000 -s 100 -crtr;
python3 pvals.py -i ../../RSTraffic/data/tract_agg_mean_crash_vs_traffic.csv -o ../../RSTraffic/data/crashes_vs_traffic_trips_price_pvals.json -p 1000 -s 100;
python3 pvals.py -i ../../RSTraffic/data/tract_agg_mean_crash_vs_traffic.csv -o ../../RSTraffic/data/crashes_vs_traffic_trips_freq_pvals.json -p 1000 -s 100 -c;
python3 pvals.py -i ../../RSTraffic/data/tract_agg_mean_crash_vs_traffic.csv -o ../../RSTraffic/data/crashes_vs_traffic_trips_time_pvals.json -p 1000 -s 100 -t;

cd ..;
