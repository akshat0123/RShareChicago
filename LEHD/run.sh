# Merge LEHD data with ridehailing + census data
cd src;
python3 merge.py;
cd ..;

cd ../RShare/analysis;

# Calculate bias on arts/entertainment jobs (resident)
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_wac.csv -o ../../LEHD/data/bias_jobs_wac.csv -b "Art_Food_Jobs"
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_wac.csv -o ../../LEHD/data/bias_jobs_wac_pickup_fare.csv -b "Pickup Fare/Mi"
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_wac.csv -o ../../LEHD/data/bias_jobs_wac_dropoff_fare.csv -b "Dropoff Fare/Mi"
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_wac.csv -o ../../LEHD/data/bias_jobs_wac_pickup_freq.csv -b "Pickup Count"
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_wac.csv -o ../../LEHD/data/bias_jobs_wac_dropoff_freq.csv -b "Dropoff Count"
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_wac.csv -o ../../LEHD/data/bias_jobs_wac_pickup_time.csv -b "Pickup Sec/Mi"
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_wac.csv -o ../../LEHD/data/bias_jobs_wac_dropoff_time.csv -b "Dropoff Sec/Mi"

# Calculate pvals on arts/entertainment jobs (resident)
python3 pvals.py -i ../../LEHD/data/tract_agg_mean_jobs_wac.csv -o ../../LEHD/data/jobs_wac_trips_jobs_pvals.json -p 1000 -s 100 -jb;
python3 pvals.py -i ../../LEHD/data/tract_agg_mean_jobs_wac.csv -o ../../LEHD/data/jobs_wac_trips_price_pvals.json -p 1000 -s 100;
python3 pvals.py -i ../../LEHD/data/tract_agg_mean_jobs_wac.csv -o ../../LEHD/data/jobs_wac_trips_freq_pvals.json -p 1000 -s 100 -c;
python3 pvals.py -i ../../LEHD/data/tract_agg_mean_jobs_wac.csv -o ../../LEHD/data/jobs_wac_trips_time_pvals.json -p 1000 -s 100 -t;

# Calculate bias on arts/entertainment jobs (workplace)
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_rac.csv -o ../../LEHD/data/bias_jobs_rac.csv -b "Art_Food_Jobs"
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_rac.csv -o ../../LEHD/data/bias_jobs_rac_pickup_fare.csv -b "Pickup Fare/Mi"
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_rac.csv -o ../../LEHD/data/bias_jobs_rac_dropoff_fare.csv -b "Dropoff Fare/Mi"
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_rac.csv -o ../../LEHD/data/bias_jobs_rac_pickup_freq.csv -b "Pickup Count"
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_rac.csv -o ../../LEHD/data/bias_jobs_rac_dropoff_freq.csv -b "Dropoff Count"
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_rac.csv -o ../../LEHD/data/bias_jobs_rac_pickup_time.csv -b "Pickup Sec/Mi"
python3 bias.py -i ../../LEHD/data/tract_agg_mean_jobs_rac.csv -o ../../LEHD/data/bias_jobs_rac_dropoff_time.csv -b "Dropoff Sec/Mi"

# Calculate pvals on arts/entertainment jobs (workplace)
python3 pvals.py -i ../../LEHD/data/tract_agg_mean_jobs_rac.csv -o ../../LEHD/data/jobs_rac_trips_jobs_pvals.json -p 1000 -s 100 -jb;
python3 pvals.py -i ../../LEHD/data/tract_agg_mean_jobs_rac.csv -o ../../LEHD/data/jobs_rac_trips_price_pvals.json -p 1000 -s 100;
python3 pvals.py -i ../../LEHD/data/tract_agg_mean_jobs_rac.csv -o ../../LEHD/data/jobs_rac_trips_freq_pvals.json -p 1000 -s 100 -c;
python3 pvals.py -i ../../LEHD/data/tract_agg_mean_jobs_rac.csv -o ../../LEHD/data/jobs_rac_trips_time_pvals.json -p 1000 -s 100 -t;

cd ..;
