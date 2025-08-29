#!/usr/bin/env python3
"""
Enhanced ACNC Agent - Two-Stage Data Collection
Stage 1: Get charity data from ACNC CSV register
Stage 2: Scrape individual charity profile pages for phone/email details
"""

import pandas as pd
import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from io import StringIO

class EnhancedACNCAgent:
    def __init__(self):
        # ACNC dataset URL from data.gov.au API
        self.main_register_url = "https://data.gov.au/data/dataset/b050b242-4487-4306-abf5-07ca073e5594/resource/8fb32972-24e9-4c95-885e-7140be51be8a/download/datadotgov_main.csv"
        self.acnc_base_url = "https://www.acnc.gov.au"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-ACNC-Agent/1.0)'
        })
    
    def get_charity_register_data(self, location_filter=None):
        """Stage 1: Get charity data from ACNC register CSV"""
        print("Stage 1: Downloading ACNC Charity Register...")
        
        try:
            response = self.session.get(self.main_register_url, timeout=60)
            response.raise_for_status()
            
            df = pd.read_csv(StringIO(response.text), low_memory=False)
            print(f"Downloaded {len(df)} total charity records")
            
            # Filter by location if specified
            if location_filter:
                location_cols = ['Address_Line_1', 'Address_Line_2', 'Town_City']
                print(f"Filtering for '{location_filter}' in address fields")
                
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
    
    def build_profile_url(self, abn):
        """Build ACNC profile URL from ABN"""
        # ACNC uses a specific URL pattern for charity profiles
        # We need to search for the charity first, then get the actual profile URL
        search_url = f"{self.acnc_base_url}/charity/charities?abn={abn}"
        return search_url
    
    def get_charity_profile_url(self, charity_name, abn):
        """Get the actual profile URL for a charity"""
        try:
            # Try direct search by ABN first
            search_url = f"{self.acnc_base_url}/charity/charities?abn={abn}"
            print(f"  Searching for profile URL: {charity_name}")
            
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for profile links in search results
            profile_links = soup.find_all('a', href=True)
            for link in profile_links:
                href = link.get('href')
                if href and '/charity/charities/' in href and '/profile' in href:
                    return urljoin(self.acnc_base_url, href)
            
            print(f"  No profile URL found for {charity_name}")
            return None
            
        except Exception as e:
            print(f"  Error finding profile URL for {charity_name}: {e}")
            return None
    
    def scrape_charity_profile(self, charity_name, profile_url):
        """Stage 2: Scrape individual charity profile for contact details"""
        contact_details = {
            'email': '',
            'phone': '',
            'website': '',
            'address_for_service': ''
        }
        
        try:
            print(f"  Scraping profile: {charity_name}")
            response = self.session.get(profile_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, page_text)
            if emails:
                # Filter out ACNC system emails
                filtered_emails = [email for email in emails 
                                 if not any(exclude in email.lower() for exclude in 
                                          ['acnc.gov.au', 'noreply', 'no-reply'])]
                if filtered_emails:
                    contact_details['email'] = filtered_emails[0]
            
            # Extract phone numbers - Australian formats
            phone_patterns = [
                r'(\(0[2-8]\)\s*\d{4}\s*\d{4})',     # (0X) XXXX XXXX
                r'(0[2-8]\s*\d{4}\s*\d{4})',         # 0X XXXX XXXX
                r'(\+61\s*[2-8]\s*\d{4}\s*\d{4})',   # +61 X XXXX XXXX
                r'(1800\s*\d{3}\s*\d{3})',           # 1800 XXX XXX
                r'(1300\s*\d{3}\s*\d{3})',           # 1300 XXX XXX
                r'(13\s*\d{2}\s*\d{2})',             # 13 XX XX
            ]
            
            for pattern in phone_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    contact_details['phone'] = matches[0].strip()
                    break
            
            # Extract website (look for structured data)
            # Look for website in the charity details section
            website_links = soup.find_all('a', href=True)
            for link in website_links:
                href = link.get('href')
                if href and href.startswith('http') and 'acnc.gov.au' not in href:
                    # Skip common non-charity websites
                    if not any(skip in href.lower() for skip in 
                              ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube']):
                        contact_details['website'] = href
                        break
            
            print(f"    -> Email: {contact_details['email']}")
            print(f"    -> Phone: {contact_details['phone']}")
            print(f"    -> Website: {contact_details['website']}")
            
        except Exception as e:
            print(f"    Error scraping {charity_name}: {e}")
        
        return contact_details
    
    def enhance_charity_data(self, df):
        """Enhance charity data with contact details from profile pages"""
        print("\nStage 2: Scraping individual charity profiles...")
        
        enhanced_data = []
        
        for idx, row in df.iterrows():
            charity_name = row.get('Charity_Legal_Name', '')
            abn = str(row.get('ABN', '')).replace('.0', '')  # Remove .0 from ABN
            
            print(f"\nProcessing {idx+1}/{len(df)}: {charity_name}")
            
            # Build basic charity info from register data
            charity_info = {
                'charity_name': charity_name,
                'abn': abn,
                'charity_size': row.get('Charity_Size', ''),
                'registration_date': row.get('Registration_Date', ''),
                'register_website': self.clean_website(str(row.get('Charity_Website', ''))),
                'address_line_1': row.get('Address_Line_1', ''),
                'town_city': row.get('Town_City', ''),
                'state': row.get('State', ''),
                'postcode': row.get('Postcode', ''),
                'email': '',
                'phone': '',
                'profile_website': '',
                'source': 'ACNC Enhanced'
            }
            
            # Get profile URL and scrape contact details
            profile_url = self.get_charity_profile_url(charity_name, abn)
            
            if profile_url:
                contact_details = self.scrape_charity_profile(charity_name, profile_url)
                charity_info.update({
                    'email': contact_details['email'],
                    'phone': contact_details['phone'],
                    'profile_website': contact_details['website']
                })
                charity_info['profile_url'] = profile_url
            else:
                charity_info['profile_url'] = 'Not found'
            
            enhanced_data.append(charity_info)
            
            # Be respectful with rate limiting
            time.sleep(2)
        
        return enhanced_data
    
    def clean_website(self, website_text):
        """Clean and standardize website URLs"""
        if not website_text or website_text.lower() in ['nan', 'none']:
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
    
    def get_enhanced_charity_data(self, location):
        """Complete two-stage charity data collection"""
        print(f"Enhanced ACNC Agent - Location: {location}")
        print("=" * 50)
        
        # Stage 1: Get charity register data
        df = self.get_charity_register_data(location_filter=location)
        
        if df is None or len(df) == 0:
            print(f"No charities found for location: {location}")
            return []
        
        # Stage 2: Enhance with profile data
        enhanced_data = self.enhance_charity_data(df)
        
        return enhanced_data
    
    def save_to_csv(self, charities, filename):
        """Save enhanced charity data to CSV"""
        if not charities:
            print("No charity data to save")
            return
        
        df = pd.DataFrame(charities)
        df.to_csv(filename, index=False)
        print(f"\nSaved {len(charities)} enhanced charity records to {filename}")
        
        # Show summary statistics
        with_email = len(df[df['email'] != ''])
        with_phone = len(df[df['phone'] != ''])
        with_website = len(df[(df['register_website'] != '') | (df['profile_website'] != '')])
        
        print(f"\nEnhancement Summary:")
        print(f"  Total charities: {len(charities)}")
        print(f"  With Email: {with_email} ({with_email/len(charities)*100:.1f}%)")
        print(f"  With Phone: {with_phone} ({with_phone/len(charities)*100:.1f}%)")
        print(f"  With Website: {with_website} ({with_website/len(charities)*100:.1f}%)")

def main():
    """Main execution function"""
    print("Enhanced ACNC Agent - Two-Stage Data Collection")
    print("=" * 50)
    
    agent = EnhancedACNCAgent()
    
    # Test with Picton (limit to first 5 for testing)
    location = "picton"
    enhanced_data = agent.get_enhanced_charity_data(location)
    
    if enhanced_data:
        filename = f"acnc_enhanced_{location}.csv"
        agent.save_to_csv(enhanced_data, filename)
        
        print(f"\nSample enhanced data:")
        for i, charity in enumerate(enhanced_data[:3]):
            print(f"\n{i+1}. {charity['charity_name']}")
            if charity['email']:
                print(f"   Email: {charity['email']}")
            if charity['phone']:
                print(f"   Phone: {charity['phone']}")
            if charity['register_website']:
                print(f"   Website (Register): {charity['register_website']}")
            if charity['profile_website']:
                print(f"   Website (Profile): {charity['profile_website']}")
    else:
        print(f"No enhanced data collected for {location}")

if __name__ == "__main__":
    main()