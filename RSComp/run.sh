# Preprocess Ricci and German Credit datasets
cd format_data;
python3 preprocessing_german.py;
python3 preprocessing_ricci.py;
cd ..;

# Calculate bias for Ricci and German Credit datasets
cd analysis;
python3 bias_ricci.py;
python3 bias_german.py;
cd ..;
