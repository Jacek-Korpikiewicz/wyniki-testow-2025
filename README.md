# Wyniki Testów 2025

This repository contains analysis of Polish school test results from 2025.

## Files

- `wyniki_testow.csv` - Original dataset with test results
- `wyniki_testow_fixed.csv` - Cleaned dataset with proper numerical formatting
- `1.ipynb` - Jupyter notebook for data analysis

## Data Description

The dataset contains test results from Polish schools including:
- Polish language test results (mean, std dev, median, mode)
- Mathematics test results (mean, std dev, median, mode)  
- English language test results (mean, std dev, median, mode)
- School information (location, type, etc.)

## Data Issues Fixed

The original CSV file had decimal numbers using comma separators (European format) which prevented proper numerical operations in Python. The fixed version converts these to dot separators for proper numerical processing.

## Usage

```python
import pandas as pd

# Load the cleaned data
df = pd.read_csv('wyniki_testow_fixed.csv')

# Now all numerical operations work correctly
print(df['mean_polski'].sum())
print(df['mean_matematyka'].mean())
```
