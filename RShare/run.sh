#############################################
########## RIDESHARE PREPROCESSING ##########
#############################################
# Split Trip data
cd data/trips;
chmod a+x split_trips.sh;
sh split_trips.sh;
cd ../../;

# Merge ACS Data
cd format_data;
total_count=$(ls ../data/trips/split | wc -l);
current_count=1;
for f in ../data/trips/split/*
do
    IFS="/" read -r -a paths <<< $f
    IFS="." read -r -a paths <<< ${paths[-1]}
    echo "echo 'Formatting $current_count / $total_count';" >> extend.sh;
    echo "python3 merge_data.py -i $f -o ../data/trips/extended/${paths[0]}_ext.csv;" >> extend.sh;
    current_count=$((current_count + 1));
done
chmod a+x extend.sh;
sh extend.sh;
rm extend.sh;
cd ..;

# Preprocess Data
cd format_data;
total_count=$(ls ../data/trips/extended | wc -l);
current_count=1;
for f in ../data/trips/extended/*
do
    IFS="/" read -r -a paths <<< $f
    IFS="." read -r -a paths <<< ${paths[-1]}
    echo "Merging $current_count / $total_count";
    python3 preprocess.py -i $f -o ../data/trips/preprocessed/${paths[0]}_pp.csv -m ../data/trips/tripcols.json
    current_count=$((current_count + 1));
done
cd ..;

# Aggregate Data Across Census Tracts
cd format_data;
total_count=$(ls ../data/trips/preprocessed | wc -l);
current_count=1;
for f in ../data/trips/preprocessed/*
do
    IFS="/" read -r -a paths <<< $f
    IFS="." read -r -a paths <<< ${paths[-1]}
    echo "Aggregating $current_count / $total_count"
    python3 tract_agg_sum_map.py -i $f -o ../data/trips/aggregate/${paths[0]}_agg.csv -k Rideshare
    current_count=$((current_count + 1));
done

infile=" ";
for f in ../data/trips/aggregate/*.csv
do
    infile+=" "
    infile+=$f
done
echo $infile;
python3 tract_agg_sum_reduce.py -i $infile -o trips_agg_mean.csv
mv trips_agg_mean.csv ../data/trips/final;
cd ..;

########################################
########## TAXI PREPROCESSING ##########
########################################
# Split Taxi data
cd data/taxi;
chmod a+x split_taxi.sh;
sh split_taxi.sh;
cd ../../;

# Merge ACS Data
cd format_data;
total_count=$(ls ../data/taxi/split | wc -l);
current_count=1;
for f in ../data/taxi/split/*
do
    IFS="/" read -r -a paths <<< $f
    IFS="." read -r -a paths <<< ${paths[-1]}
    echo "echo 'Formatting $current_count / $total_count';" >> extend.sh;
    echo "python3 merge_data.py -i $f -o ../data/taxi/extended/${paths[0]}_ext.csv;" >> extend.sh;
    current_count=$((current_count + 1));
done
chmod a+x extend.sh;
sh extend.sh;
rm extend.sh;
cd ..;

# Preprocess Data
cd format_data;
total_count=$(ls ../data/taxi/extended | wc -l);
current_count=1;
for f in ../data/taxi/extended/*
do
    IFS="/" read -r -a paths <<< $f
    IFS="." read -r -a paths <<< ${paths[-1]}
    echo "Merging $current_count / $total_count"
    python3 preprocess.py -i $f -o ../data/taxi/preprocessed/${paths[0]}_pp.csv -m ../data/taxi/taxicols.json
    current_count=$((current_count + 1));
done
cd ..;
#
# Remove Taxi outliers
cd format_data;
total_count=$(ls ../data/taxi/preprocessed | wc -l);
current_count=1;
for f in ../data/taxi/preprocessed/*
do
    IFS="/" read -r -a paths <<< $f
    IFS="." read -r -a paths <<< ${paths[-1]}
    echo "echo 'Removing Outliers $current_count / $total_count';" >> outliers.sh;
    echo "python3 remove_taxi_outliers.py -i $f -o ../data/taxi/preprocessed/${paths[0]}_or.csv;" >> outliers.sh;
    current_count=$((current_count + 1));
done
chmod a+x outliers.sh;
sh outliers.sh;
rm outliers.sh;
for f in ../data/taxi/preprocessed/*
do
    if [[ $f != *"or"* ]]; then
        rm $f
    fi
done
cd ..;
 
# Aggregate Data Across Census Tracts
cd format_data;
total_count=$(ls ../data/taxi/preprocessed | wc -l);
current_count=1;
for f in ../data/taxi/preprocessed/*
do
    IFS="/" read -r -a paths <<< $f
    IFS="." read -r -a paths <<< ${paths[-1]}
    echo "Aggregating $current_count / $total_count"
    python3 tract_agg_sum_map.py -i $f -o ../data/taxi/aggregate/${paths[0]}_agg.csv -k Taxi
    current_count=$((current_count + 1));
done

infile=" ";
for f in ../data/taxi/aggregate/*.csv
do
    infile+=" "
    infile+=$f
done
echo $infile;
python3 tract_agg_sum_reduce.py -i $infile -o taxi_agg_mean.csv
mv taxi_agg_mean.csv ../data/taxi/final;
cd ..;

#######################################
########## BIAS CALCULATIONS ##########
#######################################
cd analysis;

# Rideshare price bias calculation
python3 bias.py -i ../data/trips/final/trips_agg_mean.csv -o ../data/analysis/trips_price_pickup.csv -b "Pickup Fare/Mi";
python3 bias.py -i ../data/trips/final/trips_agg_mean.csv -o ../data/analysis/trips_price_dropoff.csv -b "Dropoff Fare/Mi";

# Rideshare pickup bias calculation
python3 bias.py -i ../data/trips/final/trips_agg_mean.csv -o ../data/analysis/trips_freq_pickup.csv -b "Pickup Count";
python3 bias.py -i ../data/trips/final/trips_agg_mean.csv -o ../data/analysis/trips_freq_dropoff.csv -b "Dropoff Count";

# Rideshare time bias calculation
python3 bias.py -i ../data/trips/final/trips_agg_mean.csv -o ../data/analysis/trips_time_pickup.csv -b "Pickup Sec/Mi";
python3 bias.py -i ../data/trips/final/trips_agg_mean.csv -o ../data/analysis/trips_time_dropoff.csv -b "Dropoff Sec/Mi";

# # Rideshare pval calculations
# python3 pvals.py -i ../data/trips/final/trips_agg_mean.csv -o ../data/analysis/trips_price_pvals.json -p 10000 -s 1000;
# python3 pvals.py -i ../data/trips/final/trips_agg_mean.csv -o ../data/analysis/trips_freq_pvals.json -p 10000 -s 1000 -c;
# python3 pvals.py -i ../data/trips/final/trips_agg_mean.csv -o ../data/analysis/trips_time_pvals.json -p 10000 -s 1000 -t;

# Rideshare effect size charts
python3 direction.py -i '../data/trips/final/trips_agg_mean.csv' -o '../data/analysis/charts/price_pickup.png' -b 'Pickup Fare/Mi';
python3 direction.py -i '../data/trips/final/trips_agg_mean.csv' -o '../data/analysis/charts/price_dropoff.png' -b 'Dropoff Fare/Mi';
python3 direction.py -i '../data/trips/final/trips_agg_mean.csv' -o '../data/analysis/charts/freq_pickup.png' -b 'Pickup Count';
python3 direction.py -i '../data/trips/final/trips_agg_mean.csv' -o '../data/analysis/charts/freq_dropoff.png' -b 'Dropoff Count';
python3 direction.py -i '../data/trips/final/trips_agg_mean.csv' -o '../data/analysis/charts/time_pickup.png' -b 'Pickup Sec/Mi';
python3 direction.py -i '../data/trips/final/trips_agg_mean.csv' -o '../data/analysis/charts/time_dropoff.png' -b 'Dropoff Sec/Mi';

# Taxi price bias calculation
python3 bias.py -i ../data/taxi/final/taxi_agg_mean.csv -o ../data/analysis/taxi_price_pickup.csv -b "Pickup Fare/Mi";
python3 bias.py -i ../data/taxi/final/taxi_agg_mean.csv -o ../data/analysis/taxi_price_dropoff.csv -b "Dropoff Fare/Mi";

# Taxi pickup bias calculation
python3 bias.py -i ../data/taxi/final/taxi_agg_mean.csv -o ../data/analysis/taxi_freq_pickup.csv -b "Pickup Count";
python3 bias.py -i ../data/taxi/final/taxi_agg_mean.csv -o ../data/analysis/taxi_freq_dropoff.csv -b "Dropoff Count";

# Taxi time bias calculation
python3 bias.py -i ../data/taxi/final/taxi_agg_mean.csv -o ../data/analysis/taxi_time_pickup.csv -b "Pickup Sec/Mi";
python3 bias.py -i ../data/taxi/final/taxi_agg_mean.csv -o ../data/analysis/taxi_time_dropoff.csv -b "Dropoff Sec/Mi";

# Taxi pval calculations
python3 pvals.py -i ../data/taxi/final/taxi_agg_mean.csv -o ../data//analysis/taxi_price_pvals.json -p 10000 -s 800;
python3 pvals.py -i ../data/taxi/final/taxi_agg_mean.csv -o ../data/analysis/taxi_freq_pvals.json -p 10000 -s 800 -c;
python3 pvals.py -i ../data/taxi/final/taxi_agg_mean.csv -o ../data/analysis/taxi_time_pvals.json -p 10000 -s 800 -t;
cd ..;
