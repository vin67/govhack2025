#!/usr/bin/env python3
"""
Test NSW Government agency page access
"""

import requests
from bs4 import BeautifulSoup
import re

def test_nsw_agency_page():
    """Test accessing a known NSW agency page"""
    
    # From your screenshot, we know Aboriginal Affairs exists
    # Let's try different URL patterns
    test_urls = [
        "https://www.service.nsw.gov.au/organisation/aboriginal-affairs",
        "https://www.service.nsw.gov.au/organisation/aboriginal-affairs-nsw",  
        "https://www.nsw.gov.au/departments-and-agencies/aboriginal-affairs",
        "https://www.nsw.gov.au/departments-and-agencies/aboriginal-affairs-nsw",
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-Test/1.0)'
    })
    
    for url in test_urls:
        print(f"Testing: {url}")
        
        try:
            response = session.get(url, timeout=30)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                page_text = soup.get_text()
                
                # Look for contact indicators
                if 'Aboriginal Affairs' in page_text:
                    print(f"  ✓ Found Aboriginal Affairs content")
                    
                    # Quick search for contact info
                    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
                    phones = re.findall(r'(\(0[2-8]\)\s*\d{4}\s*\d{4}|1800\s*\d{3}\s*\d{3})', page_text)
                    
                    if emails:
                        print(f"  ✓ Found emails: {emails[:2]}")
                    if phones:
                        print(f"  ✓ Found phones: {phones[:2]}")
                    
                    # Look for website link
                    links = soup.find_all('a', href=True)
                    for link in links[:5]:  # Check first few links
                        href = link.get('href')
                        if href and 'nsw.gov.au' in href and 'aboriginal' in href.lower():
                            print(f"  ✓ Found website link: {href}")
                            break
                    
                    print(f"  SUCCESS: This URL works!")
                    return url
                
        except Exception as e:
            print(f"  Error: {e}")
        
        print()
    
    return None

if __name__ == "__main__":
    print("Testing NSW Government Agency Page Access")
    print("=" * 50)
    working_url = test_nsw_agency_page()
    
    if working_url:
        print(f"✓ Found working URL pattern: {working_url}")
    else:
        print("✗ No working URL found")