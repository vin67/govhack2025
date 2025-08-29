#!/usr/bin/env python3
"""
Data Standardizer - Common Format Generator
Converts all agent outputs to a standardized contact format for Critic Agent review
"""

import pandas as pd
import csv
import json
from pathlib import Path
from datetime import datetime
import re

class DataStandardizer:
    def __init__(self):
        self.standard_columns = [
            'contact_id',           # Unique identifier
            'contact_type',         # phone/email/website  
            'contact_value',        # The actual contact (phone number, email, URL)
            'organization_name',    # Name of organization
            'organization_type',    # government/hospital/charity/threat
            'source_agent',         # Which agent collected this
            'source_url',          # Original source URL
            'address',             # Physical address if available
            'suburb',              # Suburb/city
            'state',               # State
            'postcode',            # Postcode
            'services',            # Services offered
            'verified_date',       # When this was collected
            'confidence_score',    # Data quality score (0-1)
            'notes'                # Additional metadata
        ]
        
        self.output_file = 'standardized_contacts.csv'
        
    def standardize_government_services(self):
        """Standardize federal government services data"""
        filepath = Path('government_services.csv')
        if not filepath.exists():
            print(f"  ✗ {filepath} not found")
            return []
            
        print(f"  Processing government services...")
        df = pd.read_csv(filepath)
        standardized = []
        
        for idx, row in df.iterrows():
            # Create phone contact record - using correct column name 'phone_number'
            phone_col = row.get('phone_number', row.get('phone', ''))
            if pd.notna(phone_col) and str(phone_col).strip():
                record = {
                    'contact_id': f"gov_phone_{idx}",
                    'contact_type': 'phone',
                    'contact_value': str(phone_col).strip(),
                    'organization_name': str(row.get('service_name', '')).strip(),
                    'organization_type': 'government',
                    'source_agent': 'government_services_scraper',
                    'source_url': str(row.get('source_url', '')),
                    'address': '',
                    'suburb': '',
                    'state': 'Federal',
                    'postcode': '',
                    'services': str(row.get('description', '')).strip(),
                    'verified_date': datetime.now().isoformat(),
                    'confidence_score': 0.9,  # High confidence - official gov source
                    'notes': f"Federal government directory - {row.get('hours_of_operation', '')}"
                }
                standardized.append(record)
        
        print(f"    Standardized {len(standardized)} government contacts")
        return standardized
    
    def standardize_nsw_services(self):
        """Standardize NSW government services data"""
        filepath = Path('nsw_correct_directory.csv')
        if not filepath.exists():
            print(f"  ✗ {filepath} not found")
            return []
            
        print(f"  Processing NSW government services...")
        df = pd.read_csv(filepath)
        standardized = []
        
        for idx, row in df.iterrows():
            # Skip the first "Listen" row which is not a real agency
            if str(row.get('agency_name', '')).strip() in ['Listen', '']:
                continue
                
            base_record = {
                'organization_name': str(row.get('agency_name', '')).strip(),
                'organization_type': 'government',
                'source_agent': 'nsw_government_scraper',
                'source_url': str(row.get('source_url', '')),
                'address': str(row.get('street_address', '')).strip(),
                'suburb': '',  # Extract from address if needed
                'state': 'NSW',
                'postcode': '',  # Extract from address if needed
                'services': '',  # NSW agencies don't have service descriptions
                'verified_date': datetime.now().isoformat(),
                'confidence_score': 0.85,  # High confidence - official NSW directory
                'notes': f"NSW Government Directory - Postal: {row.get('postal_address', '')}"
            }
            
            contact_id_base = f"nsw_gov_{idx}"
            
            # Phone contact
            if pd.notna(row.get('phone', '')) and str(row.get('phone', '')).strip():
                phone_record = base_record.copy()
                phone_record.update({
                    'contact_id': f"{contact_id_base}_phone",
                    'contact_type': 'phone',
                    'contact_value': str(row['phone']).strip()
                })
                standardized.append(phone_record)
            
            # Email contact
            if pd.notna(row.get('email', '')) and str(row.get('email', '')).strip():
                email_record = base_record.copy()
                email_record.update({
                    'contact_id': f"{contact_id_base}_email",
                    'contact_type': 'email',
                    'contact_value': str(row['email']).strip()
                })
                standardized.append(email_record)
            
            # Website contact
            if pd.notna(row.get('website', '')) and str(row.get('website', '')).strip():
                website_record = base_record.copy()
                website_record.update({
                    'contact_id': f"{contact_id_base}_website",
                    'contact_type': 'website',
                    'contact_value': str(row['website']).strip()
                })
                standardized.append(website_record)
        
        print(f"    Standardized {len(standardized)} NSW government contacts")
        return standardized
    
    def standardize_nsw_hospitals(self):
        """Standardize NSW hospitals data"""
        filepath = Path('nsw_hospitals.csv')
        if not filepath.exists():
            print(f"  ✗ {filepath} not found")
            return []
            
        print(f"  Processing NSW hospitals...")
        df = pd.read_csv(filepath)
        standardized = []
        
        for idx, row in df.iterrows():
            base_record = {
                'organization_name': str(row.get('hospital_name', '')).strip(),
                'organization_type': 'hospital',
                'source_agent': 'nsw_hospitals_agent',
                'source_url': 'NSW Health API',
                'address': str(row.get('street_address', '')).strip(),
                'suburb': str(row.get('suburb', '')).strip(),
                'state': 'NSW',
                'postcode': str(row.get('postcode', '')).strip(),
                'services': str(row.get('services', '')).strip(),
                'verified_date': datetime.now().isoformat(),
                'confidence_score': 0.95,  # Very high - official API
                'notes': f"LHD: {row.get('local_health_district', '')}"
            }
            
            contact_id_base = f"hospital_{idx}"
            
            # Phone contact
            if pd.notna(row.get('phone', '')) and str(row.get('phone', '')).strip():
                phone_record = base_record.copy()
                phone_record.update({
                    'contact_id': f"{contact_id_base}_phone",
                    'contact_type': 'phone',
                    'contact_value': str(row['phone']).strip()
                })
                standardized.append(phone_record)
            
            # Email contact
            if pd.notna(row.get('email', '')) and str(row.get('email', '')).strip():
                email_record = base_record.copy()
                email_record.update({
                    'contact_id': f"{contact_id_base}_email",
                    'contact_type': 'email',
                    'contact_value': str(row['email']).strip()
                })
                standardized.append(email_record)
            
            # Website contact
            if pd.notna(row.get('website', '')) and str(row.get('website', '')).strip():
                website_record = base_record.copy()
                website_record.update({
                    'contact_id': f"{contact_id_base}_website",
                    'contact_type': 'website',
                    'contact_value': str(row['website']).strip()
                })
                standardized.append(website_record)
        
        print(f"    Standardized {len(standardized)} hospital contacts")
        return standardized
    
    def standardize_scam_threats(self):
        """Standardize scamwatch threat data"""
        filepath = Path('scamwatch_threats.csv')
        if not filepath.exists():
            print(f"  ✗ {filepath} not found")
            return []
            
        print(f"  Processing scam threats...")
        df = pd.read_csv(filepath)
        standardized = []
        
        for idx, row in df.iterrows():
            if str(row.get('threat_value', '')).strip():
                record = {
                    'contact_id': f"threat_{idx}",
                    'contact_type': str(row.get('threat_type', '')),
                    'contact_value': str(row['threat_value']).strip(),
                    'organization_name': f"SCAM: {row.get('article_title', '')}",
                    'organization_type': 'threat',
                    'source_agent': 'scamwatch_threat_agent',
                    'source_url': str(row.get('article_url', '')),
                    'address': '',
                    'suburb': '',
                    'state': '',
                    'postcode': '',
                    'services': str(row.get('scam_tactics', '')),
                    'verified_date': datetime.now().isoformat(),
                    'confidence_score': 0.8,  # Good confidence - official scamwatch
                    'notes': f"Scam type: {row.get('scam_type', '')}, Impersonates: {row.get('impersonated_organizations', '')}"
                }
                standardized.append(record)
        
        print(f"    Standardized {len(standardized)} threat indicators")
        return standardized
    
    def standardize_charity_data(self):
        """Standardize charity data if available"""
        charity_files = [
            'verified_charity_contacts.csv',  # This has the phone numbers we extracted
            'acnc_charities_picton.csv',     # This has full charity details
            'acnc_enhanced_picton.csv'
        ]
        
        standardized = []
        
        for filename in charity_files:
            filepath = Path(filename)
            if filepath.exists():
                print(f"  Processing {filename}...")
                df = pd.read_csv(filepath)
                
                for idx, row in df.iterrows():
                    base_record = {
                        'organization_name': str(row.get('charity_name', row.get('Charity_Name', ''))).strip(),
                        'organization_type': 'charity',
                        'source_agent': 'acnc_data_agent',
                        'source_url': str(row.get('website', row.get('Website', ''))),
                        'address': str(row.get('address', row.get('Address', ''))).strip(),
                        'suburb': str(row.get('suburb', row.get('Suburb', 'Picton'))).strip(),
                        'state': 'NSW',
                        'postcode': str(row.get('postcode', row.get('Postcode', ''))).strip(),
                        'services': str(row.get('activities', row.get('Activities', ''))).strip(),
                        'verified_date': datetime.now().isoformat(),
                        'confidence_score': 0.7,  # Medium confidence - charity data
                        'notes': f"ABN: {row.get('ABN', '')}"
                    }
                    
                    contact_id_base = f"charity_{filename}_{idx}"
                    
                    # Phone contact
                    phone_col = next((col for col in df.columns if 'phone' in col.lower()), None)
                    if phone_col and pd.notna(row.get(phone_col, '')):
                        phone_record = base_record.copy()
                        phone_record.update({
                            'contact_id': f"{contact_id_base}_phone",
                            'contact_type': 'phone',
                            'contact_value': str(row[phone_col]).strip()
                        })
                        standardized.append(phone_record)
                    
                    # Email contact  
                    email_col = next((col for col in df.columns if 'email' in col.lower()), None)
                    if email_col and pd.notna(row.get(email_col, '')):
                        email_record = base_record.copy()
                        email_record.update({
                            'contact_id': f"{contact_id_base}_email",
                            'contact_type': 'email',
                            'contact_value': str(row[email_col]).strip()
                        })
                        standardized.append(email_record)
                
                break  # Use first available charity file
        
        if standardized:
            print(f"    Standardized {len(standardized)} charity contacts")
        
        return standardized
    
    def generate_standardized_dataset(self):
        """Generate complete standardized dataset"""
        print("Data Standardizer - Common Format Generator")
        print("=" * 50)
        print("Converting all agent outputs to standard format...")
        
        all_standardized = []
        
        # Process each data source
        all_standardized.extend(self.standardize_government_services())
        all_standardized.extend(self.standardize_nsw_services())
        all_standardized.extend(self.standardize_nsw_hospitals())  
        all_standardized.extend(self.standardize_scam_threats())
        all_standardized.extend(self.standardize_charity_data())
        
        if not all_standardized:
            print("No data to standardize")
            return None
        
        # Save to CSV
        df = pd.DataFrame(all_standardized, columns=self.standard_columns)
        df.to_csv(self.output_file, index=False)
        
        print(f"\nStandardized dataset saved to: {self.output_file}")
        print(f"Total records: {len(all_standardized)}")
        
        # Statistics
        stats = {}
        for contact_type in df['contact_type'].unique():
            stats[contact_type] = len(df[df['contact_type'] == contact_type])
        
        org_stats = {}
        for org_type in df['organization_type'].unique():
            org_stats[org_type] = len(df[df['organization_type'] == org_type])
        
        print(f"\nContact Type Breakdown:")
        for contact_type, count in sorted(stats.items()):
            print(f"  {contact_type}: {count}")
        
        print(f"\nOrganization Type Breakdown:")
        for org_type, count in sorted(org_stats.items()):
            print(f"  {org_type}: {count}")
        
        # Show quality scores
        avg_confidence = df['confidence_score'].mean()
        print(f"\nAverage Confidence Score: {avg_confidence:.2f}")
        
        return df

def main():
    """Main execution function"""
    standardizer = DataStandardizer()
    df = standardizer.generate_standardized_dataset()
    
    if df is not None:
        print(f"\n✅ Standardized dataset ready for Critic Agent review")
        print(f"📄 File: {standardizer.output_file}")
        print(f"📊 Schema: {len(standardizer.standard_columns)} standardized columns")

if __name__ == "__main__":
    main()