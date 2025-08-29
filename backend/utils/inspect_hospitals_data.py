#!/usr/bin/env python3
"""
Inspect the NSW hospitals API response to understand the data structure
"""

import requests
from io import StringIO
import pandas as pd

def inspect_hospitals_api():
    """Inspect the actual structure of the NSW hospitals API"""
    
    url = "https://rted-web-external.citc.health.nsw.gov.au/api/GetHospitalsReport"
    
    print("Inspecting NSW Hospitals API Response")
    print("=" * 50)
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        print(f"Status: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type')}")
        print(f"Content Length: {len(response.text)}")
        print()
        
        # Show raw content structure
        lines = response.text.split('\n')
        print("First 10 lines of response:")
        for i, line in enumerate(lines[:10]):
            print(f"{i+1:2}: {line}")
        print()
        
        # Try to find where actual CSV data starts
        csv_start_line = 0
        for i, line in enumerate(lines):
            if ',' in line and any(term in line.lower() for term in ['name', 'hospital', 'address', 'phone']):
                csv_start_line = i
                print(f"CSV data appears to start at line {i+1}: {line}")
                break
        
        if csv_start_line > 0:
            # Parse from the actual CSV start
            csv_content = '\n'.join(lines[csv_start_line:])
            df = pd.read_csv(StringIO(csv_content))
            
            print(f"\nSuccessfully parsed CSV starting from line {csv_start_line + 1}")
            print(f"DataFrame shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            print()
            
            # Show first few records
            print("First 3 hospitals:")
            for i in range(min(3, len(df))):
                print(f"\nHospital {i+1}:")
                for col in df.columns:
                    value = df.iloc[i][col]
                    if pd.notna(value) and str(value).strip():
                        print(f"  {col}: {value}")
        
        else:
            print("Could not identify CSV data structure")
            
    except Exception as e:
        print(f"Error inspecting API: {e}")

if __name__ == "__main__":
    inspect_hospitals_api()