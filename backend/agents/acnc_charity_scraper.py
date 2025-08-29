#!/usr/bin/env python3
"""
ACNC Charity Directory Scraper
Two-stage agent for extracting charity contact information
Stage 1: Get charity URLs from location search
Stage 2: Extract contact details from individual charity profiles
"""

import time
import csv
import re
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class ACNCCharityAgent:
    def __init__(self, headless=True):
        self.base_url = "https://www.acnc.gov.au"
        self.search_url = f"{self.base_url}/charity/charities"
        
        # Setup Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def search_charities_by_location(self, location):
        """Stage 1: Get charity URLs from location search"""
        charity_urls = []
        
        try:
            # Navigate to search page with location parameter
            search_url = f"{self.search_url}?location={location}"
            print(f"Searching for charities in: {location}")
            print(f"URL: {search_url}")
            
            self.driver.get(search_url)
            
            # Wait for the Vue app to load and results to appear
            time.sleep(5)
            
            # Try multiple selectors for charity links
            selectors = [
                "a[href*='/charity/charities/'][href*='/profile']",
                ".charity-link",
                "a[href*='/charity/charities/']",
                ".search-result a",
                ".charity-item a"
            ]
            
            charity_links = []
            for selector in selectors:
                try:
                    charity_links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if charity_links:
                        print(f"Found charity links with selector: {selector}")
                        break
                except Exception as e:
                    continue
            
            if not charity_links:
                # Try to get any links that look like charity profile URLs
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in all_links:
                    href = link.get_attribute("href")
                    if href and "/charity/charities/" in href and "/profile" in href:
                        charity_links.append(link)
            
            # Extract URLs
            for link in charity_links:
                href = link.get_attribute("href")
                if href and href not in charity_urls:
                    charity_urls.append(href)
                    
            print(f"Found {len(charity_urls)} charity profile URLs")
            
        except Exception as e:
            print(f"Error searching for charities: {e}")
            
        return charity_urls
    
    def extract_charity_details(self, profile_url):
        """Stage 2: Extract contact details from charity profile"""
        charity_data = {
            'name': '',
            'abn': '',
            'phone': '',
            'email': '',
            'website': '',
            'address': '',
            'charity_type': '',
            'profile_url': profile_url
        }
        
        try:
            print(f"Extracting details from: {profile_url}")
            self.driver.get(profile_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Extract charity name
            name_selectors = ["h1", ".charity-name", ".page-title", "[data-cy='charity-name']"]
            for selector in name_selectors:
                try:
                    name_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    charity_data['name'] = name_element.text.strip()
                    break
                except:
                    continue
            
            # Look for contact information in various places
            page_text = self.driver.page_source
            
            # Extract phone numbers
            phone_patterns = [
                r'(\(0[2-8]\)\s*\d{4}\s*\d{4})',  # (0X) XXXX XXXX
                r'(0[2-8]\s*\d{4}\s*\d{4})',      # 0X XXXX XXXX
                r'(1800\s*\d{3}\s*\d{3})',        # 1800 XXX XXX
                r'(1300\s*\d{3}\s*\d{3})',        # 1300 XXX XXX
                r'(13\s*\d{2}\s*\d{2})',          # 13 XX XX
            ]
            
            for pattern in phone_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    charity_data['phone'] = matches[0]
                    break
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_matches = re.findall(email_pattern, page_text)
            if email_matches:
                # Filter out common non-charity emails
                filtered_emails = [email for email in email_matches 
                                 if not any(exclude in email.lower() for exclude in 
                                          ['noreply', 'no-reply', 'donotreply', 'admin@acnc'])]
                if filtered_emails:
                    charity_data['email'] = filtered_emails[0]
            
            # Extract website URLs
            website_patterns = [
                r'https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'www\.([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ]
            
            for pattern in website_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    # Filter out ACNC and common system URLs
                    filtered_sites = [site for site in matches 
                                    if not any(exclude in site.lower() for exclude in 
                                             ['acnc.gov.au', 'google', 'facebook', 'twitter', 'linkedin'])]
                    if filtered_sites:
                        charity_data['website'] = f"https://www.{filtered_sites[0]}"
                        break
            
            # Try to find ABN
            abn_pattern = r'ABN:?\s*(\d{2}\s*\d{3}\s*\d{3}\s*\d{3})'
            abn_matches = re.findall(abn_pattern, page_text)
            if abn_matches:
                charity_data['abn'] = abn_matches[0]
            
            print(f"  -> Name: {charity_data['name']}")
            print(f"  -> Phone: {charity_data['phone']}")
            print(f"  -> Email: {charity_data['email']}")
            print(f"  -> Website: {charity_data['website']}")
            
        except Exception as e:
            print(f"Error extracting charity details: {e}")
            
        return charity_data
    
    def scrape_location_charities(self, location):
        """Complete two-stage scraping for a location"""
        all_charities = []
        
        try:
            # Stage 1: Get charity URLs
            charity_urls = self.search_charities_by_location(location)
            
            if not charity_urls:
                print(f"No charity URLs found for {location}")
                return all_charities
            
            # Stage 2: Extract details from each charity
            for i, url in enumerate(charity_urls[:10]):  # Limit to first 10 for testing
                print(f"Processing charity {i+1}/{min(len(charity_urls), 10)}")
                charity_data = self.extract_charity_details(url)
                if charity_data['name']:  # Only add if we got at least the name
                    all_charities.append(charity_data)
                
                # Be respectful with timing
                time.sleep(2)
                
        except Exception as e:
            print(f"Error in scraping process: {e}")
            
        return all_charities
    
    def save_to_csv(self, charities, filename):
        """Save charity data to CSV"""
        if not charities:
            print("No charity data to save")
            return
            
        fieldnames = ['name', 'abn', 'phone', 'email', 'website', 'address', 'charity_type', 'profile_url']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(charities)
            
        print(f"Saved {len(charities)} charities to {filename}")

def main():
    """Main execution function"""
    print("ACNC Charity Directory Scraper")
    print("==============================")
    
    try:
        agent = ACNCCharityAgent(headless=True)
        
        # Test with Picton
        location = "picton"
        charities = agent.scrape_location_charities(location)
        
        if charities:
            filename = f"acnc_charities_{location}.csv"
            agent.save_to_csv(charities, filename)
            
            print(f"\nSuccessfully extracted {len(charities)} charities from {location}")
            print("\nSample data:")
            for i, charity in enumerate(charities[:3]):
                print(f"{i+1}. {charity['name']}")
                if charity['phone']:
                    print(f"   Phone: {charity['phone']}")
                if charity['email']:
                    print(f"   Email: {charity['email']}")
                if charity['website']:
                    print(f"   Website: {charity['website']}")
                print()
        else:
            print(f"No charities found for {location}")
            
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        if 'agent' in locals():
            agent.driver.quit()

if __name__ == "__main__":
    main()