#!/usr/bin/env python3
"""
NSW Government Focused Scraper
Direct scraper for known NSW government agencies using the correct URL pattern
"""

import requests
from bs4 import BeautifulSoup
import re
import csv
import time

class NSWFocusedScraper:
    def __init__(self):
        self.base_url = "https://www.nsw.gov.au/departments-and-agencies"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-NSW-Scraper/1.0)'
        })
        
        # Known NSW agencies (first 10 for testing)
        self.test_agencies = [
            'aboriginal-affairs-nsw',
            'auditor-general',
            'crime-commission',
            'environment-protection-authority',
            'fair-trading',
            'food-authority',
            'heritage-nsw',
            'industrial-relations',
            'legal-aid-nsw',
            'natural-resources-access-regulator'
        ]
    
    def extract_agency_details(self, agency_slug):
        """Extract contact details from NSW agency page"""
        url = f"{self.base_url}/{agency_slug}"
        
        print(f"Scraping: {agency_slug}")
        print(f"URL: {url}")
        
        agency_info = {
            'agency_name': agency_slug.replace('-', ' ').title(),
            'agency_slug': agency_slug,
            'website': url,
            'email': '',
            'phone': '',
            'street_address': '',
            'postal_address': '',
            'source_url': url,
            'source': 'NSW Government'
        }
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, page_text)
            
            if emails:
                # Filter for NSW government emails first, then any valid email
                nsw_emails = [email for email in emails if 'nsw.gov.au' in email]
                if nsw_emails:
                    # Clean up any formatting issues
                    clean_email = nsw_emails[0]
                    # Fix common extraction issues - remove any non-email characters at the end
                    clean_email = re.sub(r'Phone.*$', '', clean_email, flags=re.IGNORECASE)
                    clean_email = re.sub(r'[^a-zA-Z0-9@.\-_]+.*$', '', clean_email)
                    if '@' in clean_email and '.' in clean_email:
                        agency_info['email'] = clean_email
                else:
                    agency_info['email'] = emails[0]
            
            # Extract phone numbers
            phone_patterns = [
                r'(\(0[2-8]\)\s*\d{4}\s*\d{4})',     # (0X) XXXX XXXX
                r'(0[2-8]\s*\d{4}\s*\d{4})',         # 0X XXXX XXXX
                r'(\+61\s*[2-8]\s*\d{4}\s*\d{4})',   # +61 X XXXX XXXX
                r'(1800\s*\d{3}\s*\d{3})',           # 1800 XXX XXX
                r'(1300\s*\d{3}\s*\d{3})',           # 1300 XXX XXX
                r'(13\s*\d{2}\s*\d{2})',             # 13 XX XX
                r'(131\s*\d{3})',                    # 131 XXX
            ]
            
            for pattern in phone_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    agency_info['phone'] = matches[0].strip()
                    break
            
            # Look for address information in structured content
            # Search for common address patterns
            address_patterns = [
                r'Level\s+\d+.*?NSW\s+\d{4}',  # Level X, Street, Suburb NSW XXXX
                r'\d+.*?Street.*?NSW\s+\d{4}',  # XX Street, Suburb NSW XXXX
                r'PO\s+Box\s+\d+.*?NSW\s+\d{4}',  # PO Box XXX, Suburb NSW XXXX
            ]
            
            for pattern in address_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if matches:
                    # Clean up the address
                    address = matches[0].strip()
                    # Remove extra whitespace
                    address = re.sub(r'\s+', ' ', address)
                    agency_info['street_address'] = address
                    break
            
            print(f"  Email: {agency_info['email']}")
            print(f"  Phone: {agency_info['phone']}")
            print(f"  Address: {agency_info['street_address']}")
            print(f"  Status: {'✓' if agency_info['email'] or agency_info['phone'] else '✗'}")
            print()
            
        except requests.exceptions.RequestException as e:
            print(f"  Request Error: {e}")
            agency_info['agency_name'] = f"{agency_slug.replace('-', ' ').title()} (Error: {str(e)[:50]})"
        except Exception as e:
            print(f"  General Error: {e}")
            agency_info['agency_name'] = f"{agency_slug.replace('-', ' ').title()} (Parse Error)"
        
        return agency_info
    
    def scrape_test_agencies(self):
        """Scrape the first 10 test agencies"""
        print("NSW Government Focused Scraper")
        print("=" * 50)
        print(f"Testing {len(self.test_agencies)} NSW Government agencies...")
        print()
        
        agencies_data = []
        
        for i, agency_slug in enumerate(self.test_agencies):
            print(f"Processing {i+1}/{len(self.test_agencies)}: {agency_slug}")
            
            agency_info = self.extract_agency_details(agency_slug)
            agencies_data.append(agency_info)
            
            # Rate limiting
            time.sleep(2)
        
        return agencies_data
    
    def save_to_csv(self, agencies_data, filename='nsw_government_test_10.csv'):
        """Save agencies data to CSV"""
        if not agencies_data:
            print("No agencies data to save")
            return
        
        fieldnames = ['agency_name', 'agency_slug', 'website', 'email', 'phone', 'street_address', 'postal_address', 'source_url', 'source']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(agencies_data)
        
        print(f"Saved {len(agencies_data)} NSW government agencies to {filename}")
        
        # Summary statistics
        with_email = len([a for a in agencies_data if a['email']])
        with_phone = len([a for a in agencies_data if a['phone']])
        with_address = len([a for a in agencies_data if a['street_address']])
        successful = len([a for a in agencies_data if a['email'] or a['phone']])
        
        print(f"\nNSW Government Agency Results:")
        print(f"  Total agencies tested: {len(agencies_data)}")
        print(f"  Successful extractions: {successful} ({successful/len(agencies_data)*100:.1f}%)")
        print(f"  With Email: {with_email} ({with_email/len(agencies_data)*100:.1f}%)")
        print(f"  With Phone: {with_phone} ({with_phone/len(agencies_data)*100:.1f}%)")
        print(f"  With Address: {with_address} ({with_address/len(agencies_data)*100:.1f}%)")

def main():
    """Main execution function"""
    scraper = NSWFocusedScraper()
    
    agencies_data = scraper.scrape_test_agencies()
    
    if agencies_data:
        scraper.save_to_csv(agencies_data)
        
        print(f"\nSample NSW Government Agencies:")
        successful_agencies = [a for a in agencies_data if a['email'] or a['phone']]
        
        for i, agency in enumerate(successful_agencies[:5]):
            print(f"\n{i+1}. {agency['agency_name']}")
            if agency['email']:
                print(f"   Email: {agency['email']}")
            if agency['phone']:
                print(f"   Phone: {agency['phone']}")
            if agency['street_address']:
                print(f"   Address: {agency['street_address']}")
            print(f"   Website: {agency['website']}")
    else:
        print("No agencies data collected")

if __name__ == "__main__":
    main()