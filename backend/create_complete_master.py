#!/usr/bin/env python3
"""
Create complete master CSV with all contact types from all sources
"""

import pandas as pd
import os
from datetime import datetime

def create_complete_master():
    """Create complete master CSV combining all data sources"""
    
    all_records = []
    
    print("=" * 60)
    print("📊 Creating Complete Master Dataset")
    print("=" * 60)
    
    # 1. Load NSW Government Enhanced (already has phone, email, website)
    nsw_gov_file = 'data/raw/nsw_government_enhanced.csv'
    if os.path.exists(nsw_gov_file):
        df = pd.read_csv(nsw_gov_file)
        all_records.extend(df.to_dict('records'))
        print(f"✅ NSW Government: {len(df)} records loaded")
    
    # 2. Load existing sorted_contacts_master.csv for other data
    existing_master = 'data/sorted_contacts_master.csv'
    if os.path.exists(existing_master):
        df = pd.read_csv(existing_master)
        # Filter out empty contact_type records and NSW gov duplicates
        df = df[df['contact_type'].notna() & (df['contact_type'] != '')]
        df = df[~df['source_agent'].str.contains('nsw_enhanced', na=False)]
        all_records.extend(df.to_dict('records'))
        print(f"✅ Existing data: {len(df)} records loaded")
    
    # 3. Load NSW Contacts 50 (legacy format - convert to typed)
    nsw_50_file = 'data/nsw_contacts_50.csv'
    if os.path.exists(nsw_50_file):
        df = pd.read_csv(nsw_50_file)
        typed_records = []
        contact_id = 1000
        
        for _, row in df.iterrows():
            base = {
                'organization_name': row.get('organization_name', ''),
                'organization_type': row.get('organization_type', 'government'),
                'source_agent': 'nsw_contacts_50',
                'source_url': row.get('source_url', ''),
                'address': row.get('address', ''),
                'suburb': row.get('suburb', ''),
                'state': row.get('state', 'NSW'),
                'postcode': row.get('postcode', ''),
                'services': row.get('services', 'Government services'),
                'verified_date': datetime.now().isoformat(),
                'confidence_score': 0.9,
                'notes': 'NSW government contact',
                'risk_level': 'safe',
                'priority_score': 2.0,
                'geographic_region': 'NSW',
                'category': 'Official Services'
            }
            
            # Add phone record
            if pd.notna(row.get('phone')) and str(row['phone']).strip():
                typed_records.append({
                    **base,
                    'contact_id': f'nsw50_{contact_id}',
                    'contact_type': 'phone',
                    'contact_value': str(row['phone']).strip()
                })
                contact_id += 1
            
            # Add email record
            if pd.notna(row.get('email')) and str(row['email']).strip():
                typed_records.append({
                    **base,
                    'contact_id': f'nsw50_{contact_id}',
                    'contact_type': 'email',
                    'contact_value': str(row['email']).strip()
                })
                contact_id += 1
            
            # Add website record
            if pd.notna(row.get('website')) and str(row['website']).strip():
                typed_records.append({
                    **base,
                    'contact_id': f'nsw50_{contact_id}',
                    'contact_type': 'website',
                    'contact_value': str(row['website']).strip()
                })
                contact_id += 1
        
        all_records.extend(typed_records)
        print(f"✅ NSW Contacts 50: {len(df)} orgs → {len(typed_records)} typed records")
    
    # Create master DataFrame
    if all_records:
        master_df = pd.DataFrame(all_records)
        
        # Remove duplicates based on organization_name and contact_value
        master_df = master_df.drop_duplicates(subset=['organization_name', 'contact_value'], keep='first')
        
        # Sort by priority score and organization name
        master_df = master_df.sort_values(['priority_score', 'organization_name'], 
                                         ascending=[True, True])
        
        # Save to file
        output_file = 'data/sorted_contacts_master_complete.csv'
        master_df.to_csv(output_file, index=False)
        
        print("\n" + "=" * 60)
        print("📊 COMPLETE MASTER DATASET STATISTICS")
        print("=" * 60)
        print(f"Total Records: {len(master_df)}")
        
        print(f"\n📞 By Contact Type:")
        for ct, count in master_df['contact_type'].value_counts().items():
            percentage = (count / len(master_df)) * 100
            print(f"  - {ct.title()}: {count} ({percentage:.1f}%)")
        
        print(f"\n🏢 By Organization Type:")
        for ot, count in master_df['organization_type'].value_counts().head().items():
            print(f"  - {ot.title()}: {count}")
        
        print(f"\n🛡️ By Risk Level:")
        for rl, count in master_df['risk_level'].value_counts().items():
            print(f"  - {rl.title()}: {count}")
        
        print(f"\n📍 Top States:")
        for state, count in master_df['state'].value_counts().head().items():
            print(f"  - {state}: {count}")
        
        print(f"\n✅ Master file saved to: {output_file}")
        print(f"📊 Total unique organizations: {master_df['organization_name'].nunique()}")
        
        # Copy to iOS app
        ios_csv = 'ios-app-simple/DigitalGuardianSimple/nsw_contacts_complete.csv'
        master_df.to_csv(ios_csv, index=False)
        print(f"📱 Copied to iOS app: {ios_csv}")
        
        return master_df
    
    return None

if __name__ == "__main__":
    create_complete_master()