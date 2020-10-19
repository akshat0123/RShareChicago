#!/bin/bash

# Split trips file into 1 million line files (exclude header)
echo "Splitting Files"
tail -n +2 ../../../Data/taxi.csv | split -dl 10000000 - split_taxi_ --additional-suffix=.csv;

# Move split files into "split" directory
mv split_taxi*.csv split/;

# Append header to each newly created split file
echo "Adding headers"
for f in split/*
do
    head -n 1 ../../../Data/taxi.csv | cat - $f >> temp && mv temp $f;
done
