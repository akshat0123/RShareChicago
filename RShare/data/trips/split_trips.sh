#!/bin/bash

# Split trips file into 1 million line files (exclude header)
echo "Splitting Files"
tail -n +2 ../../../Data/trips.csv | split -dl 10000000 - split_trips_ --additional-suffix=.csv;

# Move split files into "split" directory
mv split_trips*.csv split/;

# Append header to each newly created split file
echo "Adding headers"
for f in split/*
do
    head -n 1 ../../../Data/trips.csv | cat - $f >> temp && mv temp $f;
done
