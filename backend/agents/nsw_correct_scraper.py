#!/usr/bin/env python3
"""
NSW Government Correct Directory Scraper
Uses the actual Service NSW directory structure: 
https://www.service.nsw.gov.au/nswgovdirectory/[agency-name]
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
import re
from urllib.parse import urljoin

class NSWCorrectScraper:
    def __init__(self):
        self.base_url = "https://www.service.nsw.gov.au"
        self.directory_url = f"{self.base_url}/nswgovdirectory/atoz"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-NSW-Scraper/1.0)'
        })
    
    def get_directory_links(self, limit=10):
        """Stage 1: Get agency links from the A-Z directory page"""
        print(f"Stage 1: Fetching NSW Government A-Z Directory...")
        print(f"URL: {self.directory_url}")
        
        try:
            response = self.session.get(self.directory_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links that go to /nswgovdirectory/
            agency_links = []
            
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                text = link.get_text().strip()
                
                # Look for directory links
                if (href and text and 
                    '/nswgovdirectory/' in href and 
                    href != '/nswgovdirectory/atoz' and  # Not the A-Z page itself
                    not href.endswith('#') and  # Not anchor links
                    len(text) > 2):  # Reasonable name length
                    
                    full_url = urljoin(self.base_url, href)
                    agency_links.append({
                        'name': text,
                        'url': full_url,
                        'slug': href.split('/')[-1]  # Extract the agency slug
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
        print(f"  URL: {agency_url}")
        
        agency_info = {
            'agency_name': agency_name,
            'website': '',
            'email': '',
            'phone': '',
            'street_address': '',
            'postal_address': '',
            'source_url': agency_url,
            'source': 'Service NSW Directory'
        }
        
        try:
            response = self.session.get(agency_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            # Extract website URL - look for official website links
            website_links = soup.find_all('a', href=True)
            for link in website_links:
                href = link.get('href')
                link_text = link.get_text().lower()
                
                # Look for official website links
                if (href and href.startswith('http') and 
                    'nsw.gov.au' in href and 
                    'nswgovdirectory' not in href and  # Not back to directory
                    ('website' in link_text or 'visit' in link_text or href.count('/') <= 4)):
                    agency_info['website'] = href
                    break
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, page_text)
            
            if emails:
                # Prefer NSW government emails
                nsw_emails = [email for email in emails if 'nsw.gov.au' in email]
                if nsw_emails:
                    clean_email = nsw_emails[0]
                    # Clean up extraction issues
                    clean_email = re.sub(r'(Phone|Tel|Fax).*$', '', clean_email, flags=re.IGNORECASE)
                    clean_email = re.sub(r'[^a-zA-Z0-9@.\-_]+.*$', '', clean_email)
                    if '@' in clean_email and '.' in clean_email:
                        agency_info['email'] = clean_email
                else:
                    agency_info['email'] = emails[0]
            
            # Extract phone numbers
            phone_patterns = [
                r'(1800\s*\d{3}\s*\d{3})',           # 1800 XXX XXX (toll-free)
                r'(1300\s*\d{3}\s*\d{3})',           # 1300 XXX XXX (local rate)
                r'(13\s*\d{2}\s*\d{2})',             # 13 XX XX
                r'(131\s*\d{3})',                    # 131 XXX
                r'(\(0[2-8]\)\s*\d{4}\s*\d{4})',     # (0X) XXXX XXXX
                r'(0[2-8]\s*\d{4}\s*\d{4})',         # 0X XXXX XXXX
                r'(\+61\s*[2-8]\s*\d{4}\s*\d{4})',   # +61 X XXXX XXXX
            ]
            
            for pattern in phone_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    agency_info['phone'] = matches[0].strip()
                    break
            
            # Extract addresses using the Service NSW page structure
            # Look for "Street address:" and "Postal address:" labels
            lines = page_text.split('\n')
            
            for i, line in enumerate(lines):
                line_clean = line.strip()
                
                # Look for street address
                if 'Street address:' in line_clean:
                    # Get the next few lines for the address
                    address_parts = []
                    for j in range(i+1, min(i+5, len(lines))):
                        addr_line = lines[j].strip()
                        if addr_line and not any(skip in addr_line.lower() for skip in 
                                               ['postal address:', 'phone:', 'email:', 'website:']):
                            address_parts.append(addr_line)
                        elif addr_line:  # Hit another field
                            break
                    if address_parts:
                        agency_info['street_address'] = ', '.join(address_parts)
                
                # Look for postal address
                elif 'Postal address:' in line_clean:
                    address_parts = []
                    for j in range(i+1, min(i+5, len(lines))):
                        addr_line = lines[j].strip()
                        if addr_line and not any(skip in addr_line.lower() for skip in 
                                               ['street address:', 'phone:', 'email:', 'website:']):
                            address_parts.append(addr_line)
                        elif addr_line:  # Hit another field
                            break
                    if address_parts:
                        agency_info['postal_address'] = ', '.join(address_parts)
            
            print(f"    Website: {agency_info['website']}")
            print(f"    Email: {agency_info['email']}")
            print(f"    Phone: {agency_info['phone']}")
            print(f"    Street Address: {agency_info['street_address']}")
            print(f"    Postal Address: {agency_info['postal_address']}")
            
        except Exception as e:
            print(f"    Error extracting details: {e}")
        
        return agency_info
    
    def scrape_nsw_directory(self, limit=10):
        """Complete two-stage scraping process"""
        print("NSW Government Correct Directory Scraper")
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
            print(f"\nProcessing {i+1}/{len(agency_links)}")
            
            agency_info = self.extract_agency_details(link['name'], link['url'])
            agencies_data.append(agency_info)
            
            # Rate limiting
            time.sleep(2)
        
        return agencies_data
    
    def save_to_csv(self, agencies_data, filename='data/raw/nsw_correct_directory.csv'):
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
        with_address = len([a for a in agencies_data if a['street_address'] or a['postal_address']])
        successful = len([a for a in agencies_data if a['email'] or a['phone'] or a['website']])
        
        print(f"\nCorrect NSW Directory Results:")
        print(f"  Total agencies scraped: {len(agencies_data)}")
        print(f"  Successful extractions: {successful} ({successful/len(agencies_data)*100:.1f}%)")
        print(f"  With Website: {with_website} ({with_website/len(agencies_data)*100:.1f}%)")
        print(f"  With Email: {with_email} ({with_email/len(agencies_data)*100:.1f}%)")
        print(f"  With Phone: {with_phone} ({with_phone/len(agencies_data)*100:.1f}%)")
        print(f"  With Address: {with_address} ({with_address/len(agencies_data)*100:.1f}%)")

def main():
    """Main execution function"""
    scraper = NSWCorrectScraper()
    
    # Test with first 10 services
    agencies_data = scraper.scrape_nsw_directory(limit=10)
    
    if agencies_data:
        scraper.save_to_csv(agencies_data)
        
        print(f"\nSample NSW Government Agencies (Correct URLs):")
        for i, agency in enumerate(agencies_data[:5]):
            print(f"\n{i+1}. {agency['agency_name']}")
            if agency['website']:
                print(f"   Website: {agency['website']}")
            if agency['email']:
                print(f"   Email: {agency['email']}")
            if agency['phone']:
                print(f"   Phone: {agency['phone']}")
            if agency['street_address']:
                print(f"   Street Address: {agency['street_address']}")
    else:
        print("No agencies data collected")

if __name__ == "__main__":
    main()