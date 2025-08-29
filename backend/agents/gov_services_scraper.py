#!/usr/bin/env python3
"""
Government Services Directory Scraper
Unstructured Data Agent for extracting service names and phone numbers
from directory.gov.au enquiry lines
"""

import requests
from bs4 import BeautifulSoup
import csv
import re
import time
from urllib.parse import urljoin

class GovServicesAgent:
    def __init__(self):
        self.base_url = "https://www.directory.gov.au"
        self.enquiry_lines_url = f"{self.base_url}/enquiry-lines"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-DataAgent/1.0)'
        })
        
    def get_letter_pages(self):
        """Get all letter pagination links"""
        letters = []
        try:
            response = self.session.get(self.enquiry_lines_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find pagination links
            pagination = soup.find('ul', class_='pagination')
            if pagination:
                for link in pagination.find_all('a'):
                    href = link.get('href')
                    if href and '/enquiry-lines/' in href:
                        letters.append(urljoin(self.base_url, href))
            
            return letters
        except Exception as e:
            print(f"Error getting letter pages: {e}")
            return []
    
    def extract_services_from_page(self, url):
        """Extract service data from a specific page"""
        services = []
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main data table
            table = soup.find('table', class_='table')
            if not table:
                return services
                
            # Extract data from table rows
            rows = table.find('tbody').find_all('tr') if table.find('tbody') else []
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    # Extract service name (first cell)
                    title_cell = cells[0]
                    title_link = title_cell.find('a')
                    service_name = title_link.get_text(strip=True) if title_link else title_cell.get_text(strip=True)
                    
                    # Extract phone number (second cell)
                    phone_cell = cells[1]
                    phone_text = phone_cell.get_text(strip=True)
                    
                    # Clean up phone number
                    phone_number = self.clean_phone_number(phone_text)
                    
                    # Extract additional info if available
                    hours = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                    description = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                    
                    if service_name and phone_number:
                        services.append({
                            'service_name': service_name,
                            'phone_number': phone_number,
                            'hours_of_operation': hours,
                            'description': description,
                            'source_url': url
                        })
                        
        except Exception as e:
            print(f"Error extracting from {url}: {e}")
            
        return services
    
    def clean_phone_number(self, phone_text):
        """Clean and standardize phone numbers"""
        if not phone_text:
            return ""
            
        # Remove "Phone:" prefix and clean up
        phone_clean = re.sub(r'Phone:\s*', '', phone_text, flags=re.IGNORECASE)
        phone_clean = re.sub(r'<br\s*/?>.*$', '', phone_clean, flags=re.IGNORECASE)
        
        # Extract phone numbers using regex
        phone_patterns = [
            r'1800\s*\d{3}\s*\d{3}',  # 1800 numbers
            r'1300\s*\d{3}\s*\d{3}',  # 1300 numbers
            r'13\s*\d{2}\s*\d{2}',    # 13 numbers
            r'131\s*\d{3}',           # 131 numbers
            r'\(0[2-8]\)\s*\d{4}\s*\d{4}',  # (0X) XXXX XXXX
            r'0[2-8]\s*\d{4}\s*\d{4}',      # 0X XXXX XXXX
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, phone_clean)
            if match:
                return match.group().strip()
                
        return phone_clean.strip()
    
    def scrape_all_services(self):
        """Scrape services from all letter pages"""
        all_services = []
        
        print("Getting letter pages...")
        letter_pages = self.get_letter_pages()
        
        if not letter_pages:
            print("No letter pages found, trying direct approach...")
            # Try direct letter URLs
            letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w']
            letter_pages = [f"{self.enquiry_lines_url}/{letter}" for letter in letters]
        
        print(f"Found {len(letter_pages)} pages to process")
        
        for i, page_url in enumerate(letter_pages):
            print(f"Processing page {i+1}/{len(letter_pages)}: {page_url}")
            services = self.extract_services_from_page(page_url)
            all_services.extend(services)
            print(f"  -> Found {len(services)} services")
            
            # Be respectful with rate limiting
            time.sleep(1)
            
        return all_services
    
    def save_to_csv(self, services, filename='government_services.csv'):
        """Save services to CSV file"""
        if not services:
            print("No services to save")
            return
            
        fieldnames = ['service_name', 'phone_number', 'hours_of_operation', 'description', 'source_url']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(services)
            
        print(f"Saved {len(services)} services to {filename}")

def main():
    """Main execution function"""
    print("Government Services Directory Scraper")
    print("=====================================")
    
    agent = GovServicesAgent()
    services = agent.scrape_all_services()
    
    if services:
        agent.save_to_csv(services)
        print(f"\nSuccessfully extracted {len(services)} government services")
        
        # Show sample of data
        print("\nSample of extracted data:")
        for i, service in enumerate(services[:5]):
            print(f"{i+1}. {service['service_name']}: {service['phone_number']}")
    else:
        print("No services extracted")

if __name__ == "__main__":
    main()