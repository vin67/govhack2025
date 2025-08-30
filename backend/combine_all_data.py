#!/usr/bin/env python3
"""
Combine all raw data files into master CSV with all contact types
"""

import pandas as pd
import os
from datetime import datetime

def combine_all_data():
    """Combine all raw CSV files into master dataset"""
    
    all_data = []
    
    # Define the raw data files to combine
    raw_files = [
        '../data/raw/nsw_government_enhanced.csv',
        '../data/raw/nsw_hospitals.csv', 
        '../data/raw/scamwatch_threats.csv',
        '../data/raw/acnc_charities_picton.csv',
        '../data/raw/government_services.csv'
    ]
    
    print("=" * 60)
    print("📊 Combining All Data Sources")
    print("=" * 60)
    
    for file_path in raw_files:
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                records_count = len(df)
                
                # Count contact types if column exists
                if 'contact_type' in df.columns:
                    phone_count = len(df[df['contact_type'] == 'phone'])
                    email_count = len(df[df['contact_type'] == 'email'])
                    website_count = len(df[df['contact_type'] == 'website'])
                    print(f"✅ Loaded {file_path}: {records_count} records")
                    print(f"   - Phone: {phone_count}, Email: {email_count}, Website: {website_count}")
                else:
                    print(f"✅ Loaded {file_path}: {records_count} records (legacy format)")
                
                all_data.append(df)
            except Exception as e:
                print(f"⚠️  Error loading {file_path}: {e}")
        else:
            print(f"❌ File not found: {file_path}")
    
    if not all_data:
        print("No data files found!")
        return None
    
    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Ensure required columns exist with defaults
    required_columns = [
        'contact_id', 'contact_type', 'contact_value', 'organization_name',
        'organization_type', 'source_agent', 'source_url', 'address',
        'suburb', 'state', 'postcode', 'services', 'verified_date',
        'confidence_score', 'notes', 'risk_level', 'priority_score',
        'geographic_region', 'category'
    ]
    
    for col in required_columns:
        if col not in combined_df.columns:
            if col == 'verified_date':
                combined_df[col] = datetime.now().isoformat()
            elif col == 'confidence_score':
                combined_df[col] = 0.8
            elif col == 'risk_level':
                combined_df[col] = 'unknown'
            elif col == 'priority_score':
                combined_df[col] = 5.0
            else:
                combined_df[col] = ''
    
    # Save master file
    output_file = '../data/sorted_contacts_master.csv'
    combined_df.to_csv(output_file, index=False)
    
    print("\n" + "=" * 60)
    print("📊 MASTER DATA STATISTICS")
    print("=" * 60)
    print(f"Total Records: {len(combined_df)}")
    
    if 'contact_type' in combined_df.columns:
        print(f"\n📞 By Contact Type:")
        for ct, count in combined_df['contact_type'].value_counts().items():
            print(f"  - {ct.title()}: {count}")
    
    if 'organization_type' in combined_df.columns:
        print(f"\n🏢 By Organization Type:")
        for ot, count in combined_df['organization_type'].value_counts().items():
            print(f"  - {ot.title()}: {count}")
    
    if 'state' in combined_df.columns:
        print(f"\n📍 By State:")
        for state, count in combined_df['state'].value_counts().head(10).items():
            print(f"  - {state}: {count}")
    
    print(f"\n✅ Master file saved to: {output_file}")
    print(f"📊 Total unique organizations: {combined_df['organization_name'].nunique()}")
    
    return combined_df

if __name__ == "__main__":
    combine_all_data()