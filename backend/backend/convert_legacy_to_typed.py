3#!/usr/bin/env python3
"""
Convert legacy contact data to typed format (phone, email, website records)
"""

import pandas as pd
import re
from datetime import datetime

def convert_legacy_to_typed_records(df, source_name):
    """Convert legacy format to typed contact records"""
    
    records = []
    contact_id_counter = 0
    
    for _, row in df.iterrows():
        org_name = row.get('organization_name') or row.get('agency_name') or row.get('name', '')
        timestamp = datetime.now().isoformat()
        
        # Base record data
        base_record = {
            'organization_name': org_name,
            'organization_type': row.get('organization_type', 'government'),
            'source_agent': source_name,
            'source_url': row.get('source_url', ''),
            'address': row.get('address') or row.get('street_address', ''),
            'suburb': row.get('suburb', ''),
            'state': row.get('state', 'NSW'),
            'postcode': row.get('postcode', ''),
            'services': row.get('services', 'Government services'),
            'verified_date': timestamp,
            'confidence_score': row.get('confidence_score', 0.85),
            'notes': row.get('notes', f'From {source_name}'),
            'risk_level': row.get('risk_level', 'safe'),
            'priority_score': row.get('priority_score', 3.0),
            'geographic_region': row.get('geographic_region', row.get('state', 'NSW')),
            'category': row.get('category', 'Official Services')
        }
        
        # Extract phone if exists
        phone = row.get('phone') or row.get('contact_phone', '')
        if phone and str(phone).strip() and str(phone).lower() != 'nan':
            records.append({
                **base_record,
                'contact_id': f'{source_name}_{contact_id_counter}',
                'contact_type': 'phone',
                'contact_value': str(phone).strip()
            })
            contact_id_counter += 1
        
        # Extract email if exists
        email = row.get('email') or row.get('contact_email', '')
        if email and str(email).strip() and str(email).lower() != 'nan':
            records.append({
                **base_record,
                'contact_id': f'{source_name}_{contact_id_counter}',
                'contact_type': 'email',
                'contact_value': str(email).strip()
            })
            contact_id_counter += 1
        
        # Extract website if exists
        website = row.get('website') or row.get('web_url', '')
        if website and str(website).strip() and str(website).lower() != 'nan':
            records.append({
                **base_record,
                'contact_id': f'{source_name}_{contact_id_counter}',
                'contact_type': 'website',
                'contact_value': str(website).strip()
            })
            contact_id_counter += 1
    
    return records

def process_all_data():
    """Process all data files and convert to typed format"""
    
    all_typed_records = []
    
    print("=" * 60)
    print("📊 Converting All Data to Typed Format")
    print("=" * 60)
    
    # Process NSW Government Enhanced (already typed)
    try:
        df = pd.read_csv('../data/raw/nsw_government_enhanced.csv')
        if 'contact_type' in df.columns:
            all_typed_records.extend(df.to_dict('records'))
            print(f"✅ NSW Government Enhanced: {len(df)} typed records")
    except:
        pass
    
    # Process NSW Hospitals
    try:
        df = pd.read_csv('../data/raw/nsw_hospitals.csv')
        if 'contact_type' not in df.columns:
            records = convert_legacy_to_typed_records(df, 'nsw_hospitals')
            all_typed_records.extend(records)
            print(f"✅ NSW Hospitals: {len(df)} rows → {len(records)} typed records")
    except Exception as e:
        print(f"⚠️  Error processing NSW Hospitals: {e}")
    
    # Process Government Services  
    try:
        df = pd.read_csv('../data/raw/government_services.csv')
        if 'contact_type' not in df.columns:
            # This file has service_name and phone_number columns
            df['organization_name'] = df.get('service_name', df.get('organization_name', ''))
            df['phone'] = df.get('phone_number', df.get('phone', ''))
            records = convert_legacy_to_typed_records(df, 'gov_services')
            all_typed_records.extend(records)
            print(f"✅ Government Services: {len(df)} rows → {len(records)} typed records")
    except Exception as e:
        print(f"⚠️  Error processing Government Services: {e}")
    
    # Process ACNC Charities
    try:
        df = pd.read_csv('../data/raw/acnc_charities_picton.csv')
        if 'contact_type' not in df.columns:
            df['organization_type'] = 'charity'
            records = convert_legacy_to_typed_records(df, 'acnc_charities')
            all_typed_records.extend(records)
            print(f"✅ ACNC Charities: {len(df)} rows → {len(records)} typed records")
    except Exception as e:
        print(f"⚠️  Error processing ACNC Charities: {e}")
    
    # Process Scamwatch Threats
    try:
        df = pd.read_csv('../data/raw/scamwatch_threats.csv')
        if 'contact_type' not in df.columns:
            df['organization_type'] = 'threat'
            df['risk_level'] = 'threat'
            records = convert_legacy_to_typed_records(df, 'scamwatch')
            all_typed_records.extend(records)
            print(f"✅ Scamwatch Threats: {len(df)} rows → {len(records)} typed records")
    except Exception as e:
        print(f"⚠️  Error processing Scamwatch: {e}")
    
    # Process NSW Correct Directory (A-Z listing)
    try:
        df = pd.read_csv('../data/raw/nsw_correct_directory.csv')
        if 'contact_type' not in df.columns:
            df['organization_name'] = df.get('agency_name', df.get('organization_name', ''))
            records = convert_legacy_to_typed_records(df, 'nsw_directory')
            all_typed_records.extend(records)
            print(f"✅ NSW Directory A-Z: {len(df)} rows → {len(records)} typed records")
    except Exception as e:
        print(f"⚠️  Error processing NSW Directory: {e}")
    
    # Create DataFrame and save
    if all_typed_records:
        master_df = pd.DataFrame(all_typed_records)
        
        # Ensure all required columns exist
        required_columns = [
            'contact_id', 'contact_type', 'contact_value', 'organization_name',
            'organization_type', 'source_agent', 'source_url', 'address',
            'suburb', 'state', 'postcode', 'services', 'verified_date',
            'confidence_score', 'notes', 'risk_level', 'priority_score',
            'geographic_region', 'category'
        ]
        
        for col in required_columns:
            if col not in master_df.columns:
                master_df[col] = ''
        
        # Save master file
        output_file = '../data/sorted_contacts_master.csv'
        master_df[required_columns].to_csv(output_file, index=False)
        
        print("\n" + "=" * 60)
        print("📊 COMPLETE MASTER DATA STATISTICS")
        print("=" * 60)
        print(f"Total Records: {len(master_df)}")
        
        print(f"\n📞 By Contact Type:")
        for ct, count in master_df['contact_type'].value_counts().items():
            percentage = (count / len(master_df)) * 100
            print(f"  - {ct.title()}: {count} ({percentage:.1f}%)")
        
        print(f"\n🏢 By Organization Type:")
        for ot, count in master_df['organization_type'].value_counts().items():
            print(f"  - {ot.title()}: {count}")
        
        print(f"\n🛡️ By Risk Level:")
        for rl, count in master_df['risk_level'].value_counts().items():
            print(f"  - {rl.title()}: {count}")
        
        print(f"\n📍 By State:")
        for state, count in master_df['state'].value_counts().head(5).items():
            print(f"  - {state}: {count}")
        
        print(f"\n✅ Master file saved to: {output_file}")
        print(f"📊 Total unique organizations: {master_df['organization_name'].nunique()}")
        print(f"🎯 Ready for iOS app integration!")
        
        return master_df
    
    return None

if __name__ == "__main__":
    process_all_data()