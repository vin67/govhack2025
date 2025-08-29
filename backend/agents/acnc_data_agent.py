#!/usr/bin/env python3
"""
ACNC Data Agent
Downloads and processes ACNC charity data from data.gov.au API
Filters by location and extracts contact information
"""

import requests
import pandas as pd
import re
from urllib.parse import urlparse

class ACNCDataAgent:
    def __init__(self):
        # ACNC dataset URLs from data.gov.au API
        self.main_register_url = "https://data.gov.au/data/dataset/b050b242-4487-4306-abf5-07ca073e5594/resource/8fb32972-24e9-4c95-885e-7140be51be8a/download/datadotgov_main.csv"
        self.ais_2023_url = "https://data.gov.au/data/dataset/ff6905d6-9d5d-4ef1-8478-72b833864fb7/resource/2b0fb746-57c5-4523-bb4c-74b7b78279d9/download/datadotgov_ais23.csv"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GovHack2025-ACNC-DataAgent/1.0'
        })
    
    def download_charity_register(self, location_filter=None):
        """Download the main ACNC charity register"""
        print("Downloading ACNC Charity Register...")
        print(f"URL: {self.main_register_url}")
        
        try:
            response = self.session.get(self.main_register_url, timeout=60)
            response.raise_for_status()
            
            # Read CSV into pandas DataFrame
            from io import StringIO
            df = pd.read_csv(StringIO(response.text), low_memory=False)
            
            print(f"Downloaded {len(df)} total charity records")
            
            # Filter by location if specified
            if location_filter:
                # Look for location in various address fields
                location_cols = [col for col in df.columns if any(term in col.lower() 
                               for term in ['address', 'suburb', 'town', 'city', 'location'])]
                
                print(f"Searching for '{location_filter}' in address fields: {location_cols}")
                
                # Create filter mask
                mask = pd.Series([False] * len(df), index=df.index)
                
                for col in location_cols:
                    if col in df.columns:
                        mask |= df[col].astype(str).str.contains(location_filter, case=False, na=False)
                
                df = df[mask]
                print(f"Found {len(df)} charities in '{location_filter}'")
            
            return df
            
        except Exception as e:
            print(f"Error downloading charity register: {e}")
            return None
    
    def download_ais_data(self):
        """Download the 2023 Annual Information Statement data"""
        print("Downloading ACNC 2023 AIS Data...")
        print(f"URL: {self.ais_2023_url}")
        print("Note: This is a large file (~36MB), download may take time...")
        
        try:
            response = self.session.get(self.ais_2023_url, timeout=120)
            response.raise_for_status()
            
            # Read CSV into pandas DataFrame
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            print(f"Downloaded {len(df)} AIS records")
            return df
            
        except Exception as e:
            print(f"Error downloading AIS data: {e}")
            return None
    
    def extract_contact_info(self, df):
        """Extract contact information from charity dataframe"""
        contact_data = []
        
        print("Extracting data from ACNC columns...")
        print(f"Available columns: {list(df.columns)[:10]}...") # Show first 10 columns
        
        for idx, row in df.iterrows():
            charity_info = {
                'charity_name': row.get('Charity_Legal_Name', ''),
                'abn': row.get('ABN', ''),
                'charity_size': row.get('Charity_Size', ''),
                'registration_date': row.get('Registration_Date', ''),
                'website': self.clean_website(str(row.get('Charity_Website', ''))),
                'address_line_1': row.get('Address_Line_1', ''),
                'address_line_2': row.get('Address_Line_2', ''),
                'town_city': row.get('Town_City', ''),
                'state': row.get('State', ''),
                'postcode': row.get('Postcode', ''),
                'email': '',  # Not available in ACNC register
                'phone': '',  # Not available in ACNC register
                'source': 'ACNC Register'
            }
            
            # Build full address
            address_parts = []
            for field in ['Address_Line_1', 'Address_Line_2', 'Town_City', 'State', 'Postcode']:
                value = row.get(field, '')
                if pd.notna(value) and str(value).strip() and str(value).strip() != 'nan':
                    address_parts.append(str(value).strip())
            charity_info['full_address'] = ', '.join(address_parts)
            
            # Extract charity purposes (valuable for validation)
            purposes = []
            purpose_fields = [
                'Advancing_Education', 'Advancing_Health', 'Advancing_Religion', 
                'Advancing_Culture', 'Advancing_social_or_public_welfare',
                'Preventing_or_relieving_suffering_of_animals', 'Advancing_natual_environment'
            ]
            
            for field in purpose_fields:
                if row.get(field) == 'Y':
                    purposes.append(field.replace('_', ' ').replace('Advancing ', '').title())
            
            charity_info['charity_purposes'] = ', '.join(purposes) if purposes else ''
            
            # Extract beneficiaries
            beneficiaries = []
            beneficiary_fields = [
                'Children', 'Adults', 'Aged_Persons', 'Youth', 'Families',
                'People_with_Disabilities', 'General_Community_in_Australia'
            ]
            
            for field in beneficiary_fields:
                if row.get(field) == 'Y':
                    beneficiaries.append(field.replace('_', ' ').title())
            
            charity_info['beneficiaries'] = ', '.join(beneficiaries) if beneficiaries else ''
            
            # Include all charities with names (website is bonus)
            if charity_info['charity_name'].strip():
                contact_data.append(charity_info)
        
        return contact_data
    
    def clean_phone_number(self, phone_text):
        """Clean and standardize phone numbers"""
        if not phone_text or phone_text.lower() == 'nan':
            return ""
        
        # Remove common prefixes and clean up
        phone_clean = str(phone_text).strip()
        phone_clean = re.sub(r'[^\d\s\(\)\+\-]', '', phone_clean)
        
        # Australian phone number patterns
        phone_patterns = [
            r'(\+61\s*[2-8]\s*\d{4}\s*\d{4})',   # +61 X XXXX XXXX
            r'(1800\s*\d{3}\s*\d{3})',           # 1800 XXX XXX
            r'(1300\s*\d{3}\s*\d{3})',           # 1300 XXX XXX
            r'(13\s*\d{2}\s*\d{2})',             # 13 XX XX
            r'(\(0[2-8]\)\s*\d{4}\s*\d{4})',     # (0X) XXXX XXXX
            r'(0[2-8]\s*\d{4}\s*\d{4})',         # 0X XXXX XXXX
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, phone_clean)
            if match:
                return match.group().strip()
        
        return phone_clean.strip() if phone_clean.strip() else ""
    
    def clean_website(self, website_text):
        """Clean and standardize website URLs"""
        if not website_text or website_text.lower() == 'nan':
            return ""
        
        website = str(website_text).strip()
        
        # Add https:// if no protocol
        if website and not website.startswith(('http://', 'https://')):
            if website.startswith('www.'):
                website = f"https://{website}"
            else:
                website = f"https://www.{website}"
        
        # Validate URL structure
        try:
            parsed = urlparse(website)
            if parsed.netloc:
                return website
        except:
            pass
        
        return ""
    
    def get_charities_by_location(self, location):
        """Get all charity contact information for a specific location"""
        print(f"ACNC Data Agent - Extracting Charities for: {location}")
        print("=" * 50)
        
        # Download main charity register
        df = self.download_charity_register(location_filter=location)
        
        if df is None or len(df) == 0:
            print(f"No charities found for location: {location}")
            return []
        
        print(f"\nExtracting contact information from {len(df)} charities...")
        contact_data = self.extract_contact_info(df)
        
        print(f"Successfully extracted contact info for {len(contact_data)} charities")
        
        return contact_data
    
    def save_to_csv(self, charities, filename):
        """Save charity data to CSV"""
        if not charities:
            print("No charity data to save")
            return
        
        df = pd.DataFrame(charities)
        df.to_csv(filename, index=False)
        print(f"Saved {len(charities)} charities to {filename}")
        
        # Show summary statistics
        print(f"\nSummary:")
        print(f"  With Email: {len(df[df['email'] != ''])}")
        print(f"  With Phone: {len(df[df['phone'] != ''])}")
        print(f"  With Website: {len(df[df['website'] != ''])}")

def main():
    """Main execution function"""
    print("ACNC Data Agent")
    print("===============")
    
    agent = ACNCDataAgent()
    
    # Test with Picton
    location = "picton"
    charities = agent.get_charities_by_location(location)
    
    if charities:
        filename = f"acnc_charities_{location}.csv"
        agent.save_to_csv(charities, filename)
        
        print(f"\nSample data for {location}:")
        for i, charity in enumerate(charities[:5]):
            print(f"\n{i+1}. {charity['charity_name']}")
            if charity['email']:
                print(f"   Email: {charity['email']}")
            if charity['phone']:
                print(f"   Phone: {charity['phone']}")
            if charity['website']:
                print(f"   Website: {charity['website']}")
            if charity.get('charity_purposes'):
                print(f"   Purposes: {charity['charity_purposes']}")
            if charity.get('beneficiaries'):
                print(f"   Beneficiaries: {charity['beneficiaries']}")
    else:
        print(f"No charities found for {location}")

if __name__ == "__main__":
    main()