#!/usr/bin/env python3
"""
NSW Government Directory Scraper
Two-stage scraper for NSW Government services
Stage 1: Get agency links from directory A-Z page
Stage 2: Extract contact details from individual agency pages
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
import re
from urllib.parse import urljoin, urlparse

class NSWGovDirectoryScraper:
    def __init__(self):
        self.base_url = "https://www.service.nsw.gov.au"
        self.directory_url = f"{self.base_url}/nsw-government-directory"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-NSW-Scraper/1.0)'
        })
    
    def get_directory_links(self, limit=10):
        """Stage 1: Get agency links from the directory page"""
        print(f"Stage 1: Fetching NSW Government Directory...")
        print(f"URL: {self.directory_url}")
        
        try:
            response = self.session.get(self.directory_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all agency links - they appear as list items with links
            agency_links = []
            
            # Look for links within the directory sections
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                text = link.get_text().strip()
                
                # Filter for agency/department links
                if (href and text and 
                    len(text) > 5 and  # Reasonable agency name length
                    href.startswith('/') and  # Relative URL
                    'nsw-government-directory' not in href and  # Not the directory itself
                    not href.startswith('#')):  # Not an anchor link
                    
                    full_url = urljoin(self.base_url, href)
                    agency_links.append({
                        'name': text,
                        'url': full_url
                    })
            
            # Remove duplicates and limit results
            unique_links = []
            seen_urls = set()
            
            for link in agency_links:
                if link['url'] not in seen_urls and len(unique_links) < limit:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            print(f"Found {len(unique_links)} unique agency links (limited to {limit})")
            
            for i, link in enumerate(unique_links):
                print(f"{i+1:2}. {link['name']}")
                print(f"     {link['url']}")
            
            return unique_links
            
        except Exception as e:
            print(f"Error fetching directory: {e}")
            return []
    
    def extract_agency_details(self, agency_name, agency_url):
        """Stage 2: Extract contact details from individual agency page"""
        print(f"\n  Extracting details for: {agency_name}")
        
        agency_info = {
            'agency_name': agency_name,
            'website': '',
            'email': '',
            'phone': '',
            'street_address': '',
            'postal_address': '',
            'source_url': agency_url,
            'source': 'NSW Gov Directory'
        }
        
        try:
            response = self.session.get(agency_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            # Look for structured contact information
            # Method 1: Look for specific labels and their associated values
            
            # Find website
            website_labels = ['Website:', 'website:', 'Web:', 'web:']
            for label in website_labels:
                if label in page_text:
                    # Look for links near the website label
                    website_links = soup.find_all('a', href=True)
                    for link in website_links:
                        href = link.get('href')
                        if href and href.startswith('http') and 'nsw.gov.au' in href:
                            agency_info['website'] = href
                            break
                    if agency_info['website']:
                        break
            
            # Find email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, page_text)
            if emails:
                # Filter for government emails
                gov_emails = [email for email in emails if 'nsw.gov.au' in email]
                if gov_emails:
                    agency_info['email'] = gov_emails[0]
                else:
                    agency_info['email'] = emails[0]
            
            # Find phone numbers
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
            
            # Look for address information
            address_indicators = ['Street address:', 'Address:', 'Location:', 'Postal address:']
            lines = page_text.split('\n')
            
            for i, line in enumerate(lines):
                line_clean = line.strip()
                
                # Look for street address
                if any(indicator in line_clean for indicator in ['Street address:', 'Address:']):
                    # Get next few lines for address
                    address_parts = []
                    for j in range(i+1, min(i+4, len(lines))):
                        addr_line = lines[j].strip()
                        if addr_line and not any(skip in addr_line.lower() for skip in 
                                               ['phone:', 'email:', 'website:', 'fax:']):
                            address_parts.append(addr_line)
                        else:
                            break
                    if address_parts:
                        agency_info['street_address'] = ', '.join(address_parts)
                        break
            
            print(f"    Website: {agency_info['website']}")
            print(f"    Email: {agency_info['email']}")
            print(f"    Phone: {agency_info['phone']}")
            print(f"    Address: {agency_info['street_address']}")
            
        except Exception as e:
            print(f"    Error extracting details: {e}")
        
        return agency_info
    
    def scrape_nsw_directory(self, limit=10):
        """Complete two-stage scraping process"""
        print("NSW Government Directory Scraper")
        print("=" * 50)
        
        # Stage 1: Get directory links
        agency_links = self.get_directory_links(limit)
        
        if not agency_links:
            print("No agency links found")
            return []
        
        print(f"\nStage 2: Extracting contact details from {len(agency_links)} agencies...")
        
        # Stage 2: Extract details from each agency
        agencies_data = []
        
        for i, link in enumerate(agency_links):
            print(f"\nProcessing {i+1}/{len(agency_links)}: {link['name']}")
            
            agency_info = self.extract_agency_details(link['name'], link['url'])
            agencies_data.append(agency_info)
            
            # Rate limiting
            time.sleep(2)
        
        return agencies_data
    
    def save_to_csv(self, agencies_data, filename='nsw_government_agencies.csv'):
        """Save agencies data to CSV"""
        if not agencies_data:
            print("No agencies data to save")
            return
        
        fieldnames = ['agency_name', 'website', 'email', 'phone', 'street_address', 'postal_address', 'source_url', 'source']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(agencies_data)
        
        print(f"\nSaved {len(agencies_data)} NSW government agencies to {filename}")
        
        # Summary statistics
        with_website = len([a for a in agencies_data if a['website']])
        with_email = len([a for a in agencies_data if a['email']])
        with_phone = len([a for a in agencies_data if a['phone']])
        with_address = len([a for a in agencies_data if a['street_address']])
        
        print(f"\nContact Information Coverage:")
        print(f"  Total agencies: {len(agencies_data)}")
        print(f"  With Website: {with_website} ({with_website/len(agencies_data)*100:.1f}%)")
        print(f"  With Email: {with_email} ({with_email/len(agencies_data)*100:.1f}%)")
        print(f"  With Phone: {with_phone} ({with_phone/len(agencies_data)*100:.1f}%)")
        print(f"  With Address: {with_address} ({with_address/len(agencies_data)*100:.1f}%)")

def main():
    """Main execution function"""
    scraper = NSWGovDirectoryScraper()
    
    # Test with first 10 services
    agencies_data = scraper.scrape_nsw_directory(limit=10)
    
    if agencies_data:
        scraper.save_to_csv(agencies_data, 'nsw_government_test.csv')
        
        print(f"\nSample NSW Government Agencies:")
        for i, agency in enumerate(agencies_data[:5]):
            print(f"\n{i+1}. {agency['agency_name']}")
            if agency['website']:
                print(f"   Website: {agency['website']}")
            if agency['email']:
                print(f"   Email: {agency['email']}")
            if agency['phone']:
                print(f"   Phone: {agency['phone']}")
            if agency['street_address']:
                print(f"   Address: {agency['street_address']}")
    else:
        print("No agencies data collected")

if __name__ == "__main__":
    main()