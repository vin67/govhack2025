#!/usr/bin/env python3
"""
Website Contact Scraper
Scrapes contact information from charity websites we already have from ACNC register
This is often more reliable than ACNC profiles and gives us real operational contact details
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin, urlparse

class WebsiteContactScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-ContactScraper/1.0)'
        })
        self.session.timeout = 30
    
    def extract_contacts_from_website(self, website_url, charity_name):
        """Extract contact information from charity website"""
        contact_info = {
            'email': '',
            'phone': '',
            'contact_page_found': False
        }
        
        if not website_url or website_url.lower() in ['nan', 'none']:
            return contact_info
        
        try:
            print(f"  Scraping website: {website_url}")
            
            # Try to access the website
            response = self.session.get(website_url, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, page_text)
            
            if emails:
                # Filter out common system emails
                filtered_emails = [email for email in emails 
                                 if not any(exclude in email.lower() for exclude in 
                                          ['noreply', 'no-reply', 'postmaster', 'admin@', 'webmaster'])]
                if filtered_emails:
                    contact_info['email'] = filtered_emails[0]
            
            # Extract Australian phone numbers
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
                    contact_info['phone'] = matches[0].strip()
                    break
            
            # Try to find a contact page for additional information
            contact_links = soup.find_all('a', href=True)
            for link in contact_links:
                link_text = link.get_text().lower()
                href = link.get('href')
                
                if any(term in link_text for term in ['contact', 'about', 'get in touch']) and href:
                    try:
                        contact_url = urljoin(website_url, href)
                        print(f"    Found contact page: {contact_url}")
                        
                        contact_response = self.session.get(contact_url, timeout=20)
                        contact_soup = BeautifulSoup(contact_response.content, 'html.parser')
                        contact_text = contact_soup.get_text()
                        
                        # Extract additional contact info from contact page
                        if not contact_info['email']:
                            contact_emails = re.findall(email_pattern, contact_text)
                            if contact_emails:
                                filtered = [email for email in contact_emails 
                                          if not any(exclude in email.lower() for exclude in 
                                                   ['noreply', 'no-reply', 'postmaster'])]
                                if filtered:
                                    contact_info['email'] = filtered[0]
                        
                        if not contact_info['phone']:
                            for pattern in phone_patterns:
                                matches = re.findall(pattern, contact_text)
                                if matches:
                                    contact_info['phone'] = matches[0].strip()
                                    break
                        
                        contact_info['contact_page_found'] = True
                        break
                        
                    except:
                        continue
            
            print(f"    -> Email: {contact_info['email']}")
            print(f"    -> Phone: {contact_info['phone']}")
            
        except requests.exceptions.SSLError:
            print(f"    SSL error for {website_url}, skipping...")
        except requests.exceptions.Timeout:
            print(f"    Timeout for {website_url}, skipping...")
        except requests.exceptions.RequestException as e:
            print(f"    Request error for {website_url}: {str(e)[:100]}")
        except Exception as e:
            print(f"    General error for {website_url}: {str(e)[:100]}")
        
        return contact_info
    
    def enhance_charity_data_with_websites(self, csv_file_path):
        """Enhance existing charity data by scraping their websites"""
        print(f"Loading charity data from: {csv_file_path}")
        
        try:
            df = pd.read_csv(csv_file_path)
            print(f"Loaded {len(df)} charity records")
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None
        
        enhanced_data = []
        
        for idx, row in df.iterrows():
            charity_name = row.get('charity_name', '')
            website = row.get('website', '')
            
            print(f"\nProcessing {idx+1}/{len(df)}: {charity_name}")
            
            # Start with existing data
            charity_info = row.to_dict()
            
            # Add website contact information
            if website and str(website).strip() and str(website) != 'nan':
                contact_info = self.extract_contacts_from_website(website, charity_name)
                
                # Update with scraped contact info (only if not already present)
                if not charity_info.get('email') or charity_info['email'] == '':
                    charity_info['email'] = contact_info['email']
                if not charity_info.get('phone') or charity_info['phone'] == '':
                    charity_info['phone'] = contact_info['phone']
                
                charity_info['website_scraped'] = True
                charity_info['contact_page_found'] = contact_info['contact_page_found']
            else:
                charity_info['website_scraped'] = False
                charity_info['contact_page_found'] = False
                print("  No website available to scrape")
            
            enhanced_data.append(charity_info)
            
            # Rate limiting
            time.sleep(3)
        
        return enhanced_data
    
    def save_enhanced_data(self, enhanced_data, filename):
        """Save enhanced charity data"""
        if not enhanced_data:
            print("No data to save")
            return
        
        df = pd.DataFrame(enhanced_data)
        df.to_csv(filename, index=False)
        print(f"\nSaved {len(enhanced_data)} enhanced records to {filename}")
        
        # Statistics
        total = len(enhanced_data)
        with_email = len(df[df['email'] != ''])
        with_phone = len(df[df['phone'] != ''])
        websites_scraped = len(df[df['website_scraped'] == True])
        contact_pages_found = len(df[df['contact_page_found'] == True])
        
        print(f"\nWebsite Scraping Results:")
        print(f"  Total charities: {total}")
        print(f"  Websites scraped: {websites_scraped}")
        print(f"  Contact pages found: {contact_pages_found}")
        print(f"  With Email: {with_email} ({with_email/total*100:.1f}%)")
        print(f"  With Phone: {with_phone} ({with_phone/total*100:.1f}%)")

def main():
    """Main execution function"""
    print("Website Contact Scraper")
    print("=" * 30)
    
    scraper = WebsiteContactScraper()
    
    # Use the existing ACNC charity data
    input_file = "acnc_charities_picton.csv"
    enhanced_data = scraper.enhance_charity_data_with_websites(input_file)
    
    if enhanced_data:
        output_file = "acnc_picton_with_contacts.csv"
        scraper.save_enhanced_data(enhanced_data, output_file)
        
        print(f"\nSample enhanced data:")
        for i, charity in enumerate(enhanced_data[:3]):
            print(f"\n{i+1}. {charity['charity_name']}")
            if charity.get('email'):
                print(f"   Email: {charity['email']}")
            if charity.get('phone'):
                print(f"   Phone: {charity['phone']}")
            if charity.get('website'):
                print(f"   Website: {charity['website']}")

if __name__ == "__main__":
    main()