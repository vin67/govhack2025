#!/usr/bin/env python3
"""
NSW Hospitals Structured Data Agent
Downloads and processes NSW hospitals data from the official API endpoint
Pure structured data approach - CSV/API download
"""

import requests
import pandas as pd
import csv
import re
from io import StringIO

class NSWHospitalsAgent:
    def __init__(self):
        # Official NSW Health API endpoint from data.gov.au
        self.hospitals_api_url = "https://rted-web-external.citc.health.nsw.gov.au/api/GetHospitalsReport"
        
        # Alternative data.gov.au endpoint (if API fails)
        self.data_gov_url = "https://data.gov.au/data/dataset/b4573657-81dc-46e7-9677-65b607f734d4/resource/e17840df-ecfc-4e38-b51b-9f49af5dc21a/download/hospitals.csv"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-NSW-Hospitals/1.0)',
            'Accept': 'text/csv, application/json, */*'
        })
    
    def download_hospitals_data(self):
        """Download NSW hospitals data from official API"""
        print("NSW Hospitals Structured Data Agent")
        print("=" * 50)
        print(f"Downloading from NSW Health API...")
        print(f"URL: {self.hospitals_api_url}")
        
        try:
            response = self.session.get(self.hospitals_api_url, timeout=60)
            response.raise_for_status()
            
            # Determine if response is CSV or JSON
            content_type = response.headers.get('content-type', '').lower()
            
            if 'json' in content_type:
                # Handle JSON response
                data = response.json()
                df = pd.DataFrame(data)
                print(f"Downloaded JSON data with {len(df)} hospital records")
                
            else:
                # Handle CSV response with header comments
                lines = response.text.split('\n')
                
                # Find where CSV data starts (skip header comment)
                csv_start_line = 0
                for i, line in enumerate(lines):
                    if ',' in line and any(term in line.lower() for term in ['name', 'address', 'phone']):
                        csv_start_line = i
                        break
                
                # Parse CSV from actual data start
                csv_content = '\n'.join(lines[csv_start_line:])
                df = pd.read_csv(StringIO(csv_content))
                print(f"Downloaded CSV data with {len(df)} hospital records")
            
            print(f"Columns available: {list(df.columns)}")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            print("Trying alternative data source...")
            return self.download_from_data_gov()
            
        except Exception as e:
            print(f"Error processing hospital data: {e}")
            return None
    
    def download_from_data_gov(self):
        """Fallback: Try data.gov.au direct download"""
        try:
            print(f"Trying data.gov.au alternative...")
            print(f"URL: {self.data_gov_url}")
            
            response = self.session.get(self.data_gov_url, timeout=60)
            response.raise_for_status()
            
            df = pd.read_csv(StringIO(response.text))
            print(f"Downloaded {len(df)} hospital records from data.gov.au")
            print(f"Columns available: {list(df.columns)}")
            return df
            
        except Exception as e:
            print(f"Data.gov.au download also failed: {e}")
            return None
    
    def clean_and_process_hospitals(self, df):
        """Clean and process hospital data"""
        if df is None or len(df) == 0:
            print("No data to process")
            return []
        
        print(f"\nProcessing {len(df)} hospital records...")
        
        # Show first few rows to understand structure
        print(f"\nSample data structure:")
        print(df.head(2).to_string())
        
        processed_hospitals = []
        
        for idx, row in df.iterrows():
            hospital_info = {
                'hospital_name': '',
                'hospital_type': '',
                'phone': '',
                'email': '',
                'website': '',
                'street_address': '',
                'suburb': '',
                'postcode': '',
                'state': 'NSW',
                'local_health_district': '',
                'services': '',
                'source': 'NSW Health API'
            }
            
            # Map actual NSW Health API columns to our structure
            # Columns: Name, Address, Suburb, Postcode, Phone, Email Address, Fax, LHD, Hospital Website, ED
            column_mapping = {
                'hospital_name': ['Name'],
                'hospital_type': ['ED'],  # Emergency Department status can indicate hospital type
                'phone': ['Phone'],
                'email': ['Email Address'],
                'website': ['Hospital Website'],
                'street_address': ['Address'],
                'suburb': ['Suburb'],
                'postcode': ['Postcode'],
                'local_health_district': ['LHD'],
                'services': ['ED']  # ED status is a service indicator
            }
            
            # Map data using flexible column matching
            for field, possible_columns in column_mapping.items():
                for col_name in possible_columns:
                    if col_name in df.columns:
                        value = row.get(col_name, '')
                        if pd.notna(value) and str(value).strip():
                            hospital_info[field] = str(value).strip()
                        break
            
            # Clean phone numbers to Australian format
            if hospital_info['phone']:
                hospital_info['phone'] = self.clean_phone_number(hospital_info['phone'])
            
            # Clean email addresses
            if hospital_info['email']:
                hospital_info['email'] = self.clean_email(hospital_info['email'])
            
            # Build full address
            address_parts = []
            for addr_field in ['street_address', 'suburb', 'state', 'postcode']:
                if hospital_info[addr_field]:
                    address_parts.append(hospital_info[addr_field])
            hospital_info['full_address'] = ', '.join(address_parts)
            
            # Only include hospitals with at least a name
            if hospital_info['hospital_name']:
                processed_hospitals.append(hospital_info)
        
        print(f"Processed {len(processed_hospitals)} hospitals successfully")
        
        return processed_hospitals
    
    def clean_phone_number(self, phone_text):
        """Clean and standardize phone numbers"""
        if not phone_text or str(phone_text).lower() in ['nan', 'none', '']:
            return ""
        
        phone_clean = str(phone_text).strip()
        
        # Australian phone number patterns
        phone_patterns = [
            r'(\+61\s*[2-8]\s*\d{4}\s*\d{4})',   # +61 X XXXX XXXX
            r'(\(0[2-8]\)\s*\d{4}\s*\d{4})',     # (0X) XXXX XXXX
            r'(0[2-8]\s*\d{4}\s*\d{4})',         # 0X XXXX XXXX
            r'(1800\s*\d{3}\s*\d{3})',           # 1800 XXX XXX
            r'(1300\s*\d{3}\s*\d{3})',           # 1300 XXX XXX
            r'(13\s*\d{2}\s*\d{2})',             # 13 XX XX
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, phone_clean)
            if match:
                return match.group().strip()
        
        return phone_clean
    
    def clean_email(self, email_text):
        """Clean email addresses"""
        if not email_text or str(email_text).lower() in ['nan', 'none', '']:
            return ""
        
        email_clean = str(email_text).strip()
        
        # Basic email validation
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, email_clean)
        
        if match:
            return match.group()
        
        return ""
    
    def save_to_csv(self, hospitals_data, filename='data/raw/nsw_hospitals.csv'):
        """Save hospitals data to CSV"""
        if not hospitals_data:
            print("No hospitals data to save")
            return
        
        fieldnames = [
            'hospital_name', 'hospital_type', 'phone', 'email', 'website',
            'street_address', 'suburb', 'postcode', 'state', 'full_address',
            'local_health_district', 'services', 'source'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(hospitals_data)
        
        print(f"\nSaved {len(hospitals_data)} NSW hospitals to {filename}")
        
        # Summary statistics
        with_phone = len([h for h in hospitals_data if h['phone']])
        with_email = len([h for h in hospitals_data if h['email']])
        with_website = len([h for h in hospitals_data if h['website']])
        with_address = len([h for h in hospitals_data if h['full_address']])
        
        print(f"\nNSW Hospitals Data Summary:")
        print(f"  Total hospitals: {len(hospitals_data)}")
        print(f"  With Phone: {with_phone} ({with_phone/len(hospitals_data)*100:.1f}%)")
        print(f"  With Email: {with_email} ({with_email/len(hospitals_data)*100:.1f}%)")
        print(f"  With Website: {with_website} ({with_website/len(hospitals_data)*100:.1f}%)")
        print(f"  With Address: {with_address} ({with_address/len(hospitals_data)*100:.1f}%)")
        
        # Show hospital types breakdown
        hospital_types = {}
        for hospital in hospitals_data:
            htype = hospital.get('hospital_type', 'Unknown')
            hospital_types[htype] = hospital_types.get(htype, 0) + 1
        
        if hospital_types:
            print(f"\nHospital Types:")
            for htype, count in sorted(hospital_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {htype}: {count}")

def main():
    """Main execution function"""
    agent = NSWHospitalsAgent()
    
    # Download hospital data
    df = agent.download_hospitals_data()
    
    if df is not None:
        # Process and clean the data
        hospitals_data = agent.clean_and_process_hospitals(df)
        
        if hospitals_data:
            # Save to CSV
            agent.save_to_csv(hospitals_data)
            
            # Show sample hospitals
            print(f"\nSample NSW Hospitals:")
            for i, hospital in enumerate(hospitals_data[:5]):
                print(f"\n{i+1}. {hospital['hospital_name']}")
                if hospital['hospital_type']:
                    print(f"   Type: {hospital['hospital_type']}")
                if hospital['phone']:
                    print(f"   Phone: {hospital['phone']}")
                if hospital['email']:
                    print(f"   Email: {hospital['email']}")
                if hospital['full_address']:
                    print(f"   Address: {hospital['full_address']}")
                if hospital['local_health_district']:
                    print(f"   District: {hospital['local_health_district']}")
        else:
            print("No hospitals data processed")
    else:
        print("Failed to download hospital data")

if __name__ == "__main__":
    main()