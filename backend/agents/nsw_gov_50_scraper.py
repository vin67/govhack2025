#!/usr/bin/env python3
"""
NSW Government Directory Scraper - 50 Records Version
Enhanced scraper to fetch 50 NSW Government agency contacts
For GovHack 2025 - Digital Guardian Project
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
    
    def get_directory_links(self, limit=50):
        """Stage 1: Get agency links from the directory page - INCREASED TO 50"""
        print(f"Stage 1: Fetching NSW Government Directory...")
        print(f"URL: {self.directory_url}")
        print(f"Target: {limit} agencies")
        
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
            
            print(f"Found {len(unique_links)} unique agency links (target: {limit})")
            
            # Print first 10 for verification
            print("\nFirst 10 agencies found:")
            for i, link in enumerate(unique_links[:10]):
                print(f"{i+1:2}. {link['name']}")
            
            if len(unique_links) > 10:
                print(f"... and {len(unique_links) - 10} more agencies")
            
            return unique_links
            
        except Exception as e:
            print(f"Error fetching directory: {e}")
            return []
    
    def extract_agency_details(self, agency_name, agency_url):
        """Stage 2: Extract contact details from individual agency page"""
        
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
            
            # Find phone numbers - Enhanced patterns for NSW numbers
            phone_patterns = [
                r'(\(02\)\s*\d{4}\s*\d{4})',         # (02) XXXX XXXX - Sydney/NSW
                r'(02\s*\d{4}\s*\d{4})',             # 02 XXXX XXXX - Sydney/NSW
                r'(\+61\s*2\s*\d{4}\s*\d{4})',       # +61 2 XXXX XXXX - International Sydney
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
            
        except Exception as e:
            pass  # Silent fail for individual agencies to continue processing
        
        return agency_info
    
    def scrape_nsw_directory(self, limit=50):
        """Complete two-stage scraping process for 50 agencies"""
        print("NSW Government Directory Scraper - Enhanced for 50 Records")
        print("=" * 60)
        
        # Stage 1: Get directory links
        agency_links = self.get_directory_links(limit)
        
        if not agency_links:
            print("No agency links found")
            return []
        
        print(f"\nStage 2: Extracting contact details from {len(agency_links)} agencies...")
        print("This may take a few minutes due to rate limiting...")
        
        # Stage 2: Extract details from each agency
        agencies_data = []
        
        for i, link in enumerate(agency_links):
            if (i + 1) % 10 == 0:
                print(f"Progress: {i+1}/{len(agency_links)} agencies processed...")
            
            agency_info = self.extract_agency_details(link['name'], link['url'])
            
            # Only add if we found at least phone or email
            if agency_info['phone'] or agency_info['email']:
                agencies_data.append(agency_info)
            
            # Rate limiting - be respectful to the server
            time.sleep(1.5)
        
        print(f"\nCompleted: {len(agencies_data)} agencies with contact information")
        
        return agencies_data
    
    def save_to_csv(self, agencies_data, filename='nsw_government_50_agencies.csv'):
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
        
        # Print some sample data
        print(f"\nSample NSW Government Agencies with Phone Numbers:")
        phone_agencies = [a for a in agencies_data if a['phone']][:5]
        for i, agency in enumerate(phone_agencies):
            print(f"\n{i+1}. {agency['agency_name']}")
            print(f"   Phone: {agency['phone']}")
            if agency['email']:
                print(f"   Email: {agency['email']}")
            if agency['website']:
                print(f"   Website: {agency['website']}")

def main():
    """Main execution function"""
    scraper = NSWGovDirectoryScraper()
    
    # Scrape 50 NSW government agencies
    print("Starting scraper for 50 NSW Government agencies...")
    agencies_data = scraper.scrape_nsw_directory(limit=50)
    
    if agencies_data:
        # Save to data directory
        import os
        data_dir = '/Users/vinodralh/Code/claude/govhack2025/data/raw'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        output_file = os.path.join(data_dir, 'nsw_government_50_agencies.csv')
        scraper.save_to_csv(agencies_data, output_file)
        
        print(f"\n✅ Successfully scraped {len(agencies_data)} NSW Government agencies")
        print(f"📁 Data saved to: {output_file}")
    else:
        print("❌ No agencies data collected")

if __name__ == "__main__":
    main()