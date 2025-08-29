#!/usr/bin/env python3
"""
Inspect ACNC data structure to understand available fields
"""

import pandas as pd
import requests
from io import StringIO

def inspect_acnc_data():
    """Examine the structure of ACNC data"""
    
    url = "https://data.gov.au/data/dataset/b050b242-4487-4306-abf5-07ca073e5594/resource/8fb32972-24e9-4c95-885e-7140be51be8a/download/datadotgov_main.csv"
    
    print("Downloading ACNC data sample...")
    response = requests.get(url, timeout=60)
    
    # Read only first 1000 rows to understand structure
    df = pd.read_csv(StringIO(response.text), nrows=1000, low_memory=False)
    
    print(f"\nDataset shape: {df.shape}")
    print(f"Column count: {len(df.columns)}")
    
    print("\nAll available columns:")
    for i, col in enumerate(df.columns):
        print(f"{i+1:2}. {col}")
    
    print("\nSample data for Picton charities:")
    picton_mask = df['Town_City'].astype(str).str.contains('picton', case=False, na=False)
    picton_df = df[picton_mask]
    
    if len(picton_df) > 0:
        print(f"Found {len(picton_df)} Picton charities in sample")
        
        # Show first Picton charity
        charity = picton_df.iloc[0]
        print(f"\nSample charity: {charity['Charity_Name']}")
        
        # Show all non-empty fields
        for col in df.columns:
            value = charity[col]
            if pd.notna(value) and str(value).strip():
                print(f"  {col}: {value}")
    else:
        print("No Picton charities in sample")

if __name__ == "__main__":
    inspect_acnc_data()