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
from bs4 import BeautifulSoup
import time

class ACNCDataAgent:
    def __init__(self):
        # ACNC dataset URLs from data.gov.au API
        self.main_register_url = "https://data.gov.au/data/dataset/b050b242-4487-4306-abf5-07ca073e5594/resource/8fb32972-24e9-4c95-885e-7140be51be8a/download/datadotgov_main.csv"
        self.ais_2023_url = "https://data.gov.au/data/dataset/ff6905d6-9d5d-4ef1-8478-72b833864fb7/resource/2b0fb746-57c5-4523-bb4c-74b7b78279d9/download/datadotgov_ais23.csv"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-ACNC-DataAgent/1.0)'
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
                'email': '',  # Will be extracted from website
                'phone': '',  # Will be extracted from website
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
            
            # Extract contact information from official ACNC profile if available
            if charity_info['abn'] and charity_info['charity_name'].strip():
                print(f"Extracting contacts for: {charity_info['charity_name']}")
                profile_contacts = self.extract_contacts_from_acnc_profile(
                    charity_info['abn'], 
                    charity_info['charity_name']
                )
                
                # Update charity info with official ACNC contacts
                charity_info['email'] = profile_contacts.get('email', '')
                charity_info['phone'] = profile_contacts.get('phone', '')
                charity_info['website'] = profile_contacts.get('website', charity_info['website'])
                
                # Add a small delay to be respectful to ACNC servers
                time.sleep(1)
            
            # Include all charities with names (website is bonus)
            if charity_info['charity_name'].strip():
                contact_data.append(charity_info)
        
        return contact_data
    
    def search_picton_charities(self):
        """Step 1: Get Picton charities from existing CSV data"""
        print("Step 1: Getting Picton charities from existing data...")
        
        # Use existing CSV data - we already have the organizational information
        existing_csv = "data/raw/acnc_charities_picton.csv"
        charity_data = []
        
        try:
            import os
            if os.path.exists(existing_csv):
                df = pd.read_csv(existing_csv)
                print(f"Found {len(df)} charities in existing data")
                
                # Convert CSV data to the format we need
                for _, row in df.iterrows():
                    charity_record = {
                        'charity_name': row.get('charity_name', '').strip(),
                        'abn': str(row.get('abn', '')).replace('.0', '').strip(),
                        'email': row.get('email', ''),  # Usually empty from CSV
                        'phone': row.get('phone', ''),  # Usually empty from CSV  
                        'website': row.get('website', ''),  # Usually empty from CSV
                        'address': row.get('full_address', ''),
                        'suburb': 'Picton',
                        'state': row.get('state', 'NSW'),
                        'postcode': str(row.get('postcode', '')).replace('.0', ''),
                        'charity_purposes': row.get('charity_purposes', ''),
                        'registration_date': row.get('registration_date', ''),
                        'charity_size': row.get('charity_size', ''),
                        'source': 'ACNC Register (CSV Data)'
                    }
                    
                    if charity_record['charity_name']:
                        charity_data.append(charity_record)
                        print(f"  Loaded: {charity_record['charity_name']}")
                
            else:
                print("No existing CSV found. Please run the data download first.")
                return []
                
            print(f"Loaded {len(charity_data)} charity records")
            return charity_data
            
        except Exception as e:
            print(f"Error loading Picton charities: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def find_acnc_profile_by_abn(self, abn, charity_name):
        """Find ACNC profile URL by searching the charity table"""
        try:
            # Use the direct charity location search that works!
            search_url = 'https://www.acnc.gov.au/charity/charities'
            params = {'location': 'picton'}
            
            response = self.session.get(search_url, params=params, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for table rows with data-v-5f6e0f24 attributes (as shown in screenshot)
            table_rows = soup.find_all('tr', attrs={'data-v-5f6e0f24': True})
            
            for row in table_rows:
                # Look for links in this row
                for link in row.find_all('a', href=True):
                    href = link.get('href', '')
                    link_text = link.get_text().strip()
                    
                    # Check if this is a charity profile link for our charity
                    if '/charity/charities/' in href and '/profile' in href:
                        # Match by charity name (more reliable than ABN in table)
                        name_words = charity_name.lower().split()
                        link_words = link_text.lower().split()
                        
                        # Check for significant word overlap
                        if (charity_name.lower() in link_text.lower() or
                            link_text.lower() in charity_name.lower() or
                            len(set(name_words) & set(link_words)) >= 2):
                            
                            full_url = f"https://www.acnc.gov.au{href}" if href.startswith('/') else href
                            return full_url
                
                # Also check if ABN appears in the row text (less reliable but backup)
                row_text = row.get_text()
                if abn in row_text:
                    for link in row.find_all('a', href=True):
                        href = link.get('href', '')
                        if '/charity/charities/' in href and '/profile' in href:
                            full_url = f"https://www.acnc.gov.au{href}" if href.startswith('/') else href
                            return full_url
            
            return None
            
        except Exception as e:
            print(f"    Error searching for {charity_name}: {e}")
            return None
    
    def extract_contact_from_acnc_profile(self, profile_url):
        """Extract contact details from ACNC profile page"""
        contact_info = {
            'email': '',
            'phone': '',
            'website': ''
        }
        
        try:
            response = self.session.get(profile_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract email - look for mailto links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('mailto:') and 'acnc.gov.au' not in href:
                    email = href.replace('mailto:', '').strip()
                    if '@' in email:
                        contact_info['email'] = email
                        break
            
            # Extract phone - search page text for Australian phone patterns
            page_text = soup.get_text()
            phone_patterns = [
                r'(\(?0[2-8]\)?\s*\d{4}\s*\d{4})',
                r'(\+61\s*[2-8]\s*\d{4}\s*\d{4})', 
                r'(1800\s*\d{3}\s*\d{3})',
                r'(1300\s*\d{3}\s*\d{3})',
                r'(13\s*\d{2}\s*\d{2})',
            ]
            
            for pattern in phone_patterns:
                phone_matches = re.findall(pattern, page_text)
                if phone_matches:
                    # Get the first valid phone number
                    phone = phone_matches[0].strip()
                    if len(re.sub(r'\D', '', phone)) >= 8:  # At least 8 digits
                        contact_info['phone'] = phone
                        break
            
            # Extract website - look for external website links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if (href.startswith('http') and 
                    'acnc.gov.au' not in href and
                    any(indicator in href.lower() for indicator in ['.org.au', '.edu.au', '.gov.au', '.com.au', 'school'])):
                    contact_info['website'] = href
                    break
            
            # Try to find structured contact information in specific containers
            # Look for sections with contact information
            for section in soup.find_all(['div', 'section'], class_=lambda x: x and 'contact' in str(x).lower()):
                section_text = section.get_text()
                
                # Email from section
                if not contact_info['email']:
                    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                    email_match = re.search(email_pattern, section_text)
                    if email_match and 'acnc.gov.au' not in email_match.group():
                        contact_info['email'] = email_match.group()
                
                # Phone from section 
                if not contact_info['phone']:
                    for pattern in phone_patterns:
                        phone_match = re.search(pattern, section_text)
                        if phone_match:
                            contact_info['phone'] = phone_match.group().strip()
                            break
                            
        except Exception as e:
            print(f"    Error extracting from profile: {e}")
        
        return contact_info
    
    def extract_contact_from_profile(self, charity_info):
        """Step 2: Extract contact details from individual charity profile"""
        profile_url = charity_info['profile_url']
        charity_name = charity_info['name']
        
        print(f"Extracting contacts for: {charity_name}")
        
        contact_data = {
            'charity_name': charity_name,
            'abn': '',
            'email': '',
            'phone': '',
            'website': '',
            'address': '',
            'suburb': '',
            'state': '',
            'postcode': '',
            'charity_purposes': '',
            'registration_date': '',
            'charity_size': '',
            'source': 'ACNC Profile'
        }
        
        try:
            response = self.session.get(profile_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic charity information from the profile page
            # ABN - usually in a structured field
            abn_elements = soup.find_all(text=re.compile(r'ABN.*\d{11}'))
            if abn_elements:
                abn_match = re.search(r'(\d{11})', str(abn_elements[0]))
                if abn_match:
                    contact_data['abn'] = abn_match.group(1)
            
            # Address information - look for address fields
            address_parts = []
            for element in soup.find_all(['dd', 'span', 'div']):
                text = element.get_text().strip()
                if re.match(r'^\d+.*[A-Z]{2,3}\s+\d{4}$', text):  # Looks like an address
                    address_parts.append(text)
            
            if address_parts:
                full_address = address_parts[0]
                contact_data['address'] = full_address
                # Try to extract postcode and state
                postcode_match = re.search(r'([A-Z]{2,3})\s+(\d{4})$', full_address)
                if postcode_match:
                    contact_data['state'] = postcode_match.group(1)
                    contact_data['postcode'] = postcode_match.group(2)
            
            # Email - look for mailto links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('mailto:') and 'acnc.gov.au' not in href:
                    email = href.replace('mailto:', '').strip()
                    if '@' in email:
                        contact_data['email'] = email
                        break
            
            # Phone - search page text for Australian phone patterns  
            page_text = soup.get_text()
            phone_patterns = [
                r'(\(?0[2-8]\)?\s*\d{4}\s*\d{4})',
                r'(\+61\s*[2-8]\s*\d{4}\s*\d{4})',
                r'(1800\s*\d{3}\s*\d{3})',
                r'(1300\s*\d{3}\s*\d{3})',
                r'(13\s*\d{2}\s*\d{2})',
            ]
            
            for pattern in phone_patterns:
                phone_matches = re.findall(pattern, page_text)
                if phone_matches:
                    contact_data['phone'] = phone_matches[0].strip()
                    break
            
            # Website - look for external website links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if (href.startswith('http') and 
                    'acnc.gov.au' not in href and 
                    any(indicator in href.lower() for indicator in ['.org.au', '.edu.au', '.gov.au', 'school', charity_name.lower().split()[0]])):
                    contact_data['website'] = href
                    break
            
            print(f"  -> ABN: {contact_data['abn']}")
            print(f"  -> Email: {contact_data['email']}")
            print(f"  -> Phone: {contact_data['phone']}")
            print(f"  -> Website: {contact_data['website']}")
            print(f"  -> Address: {contact_data['address']}")
            
        except Exception as e:
            print(f"  Error extracting from profile: {e}")
        
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
        
        # Step 1: Get charities from existing CSV data  
        if location.lower() == 'picton':
            base_charity_data = self.search_picton_charities()
        else:
            print(f"Location '{location}' not yet supported. Currently only 'picton' is implemented.")
            return []
        
        if not base_charity_data:
            print(f"No charities found for {location}")
            return []
        
        # Step 2: For each charity, try to find and scrape their ACNC profile for contact details
        print(f"\nStep 2: Extracting contact details from {len(base_charity_data)} charity profiles...")
        complete_contact_data = []
        
        for charity_data in base_charity_data:
            print(f"\nProcessing: {charity_data['charity_name']}")
            
            # Try to find the ACNC profile URL using ABN
            abn = charity_data['abn']
            profile_url = self.find_acnc_profile_by_abn(abn, charity_data['charity_name'])
            
            if profile_url:
                print(f"  Found profile: {profile_url}")
                
                # Extract contact details from the profile
                contact_details = self.extract_contact_from_acnc_profile(profile_url)
                
                # Merge the contact details with the base charity data
                charity_data.update({
                    'email': contact_details.get('email', ''),
                    'phone': contact_details.get('phone', ''),
                    'website': contact_details.get('website', charity_data.get('website', ''))
                })
                
                print(f"  -> Email: {charity_data['email']}")
                print(f"  -> Phone: {charity_data['phone']}")
                print(f"  -> Website: {charity_data['website']}")
            else:
                print(f"  No ACNC profile found")
            
            complete_contact_data.append(charity_data)
            time.sleep(0.5)  # Be respectful to servers
        
        print(f"\nSuccessfully processed {len(complete_contact_data)} charities")
        return complete_contact_data
    
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
        filename = f"data/raw/acnc_charities_{location}.csv"
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