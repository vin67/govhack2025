#!/usr/bin/env python3
"""Test direct access to charity profiles"""

import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-ACNC-DataAgent/1.0)'
})

# We know these Picton charities from our CSV data:
test_charities = [
    {"name": "Picton High School P & C Association", "abn": "43979176197"},
    {"name": "His House Incorporated", "abn": "20160089146"},
    {"name": "Wollondilly Anglican Church", "abn": "36255906764"},
]

print("Testing direct charity profile access...")

for charity in test_charities:
    print(f"\n" + "="*50)
    print(f"Testing: {charity['name']} (ABN: {charity['abn']})")
    
    # Try to construct or find the profile URL
    # First, try searching for the charity by ABN using different methods
    
    search_methods = [
        # Method 1: Try direct ABN search 
        {
            'url': 'https://www.acnc.gov.au/search',
            'params': {'keyword': charity['abn']}
        },
        # Method 2: Try charity register with text search
        {
            'url': 'https://www.acnc.gov.au/charity/charities',
            'params': {'search_api_fulltext': charity['abn']}
        },
        # Method 3: Try with name
        {
            'url': 'https://www.acnc.gov.au/search', 
            'params': {'keyword': charity['name'].split()[0]}  # First word of name
        }
    ]
    
    profile_url = None
    
    for i, method in enumerate(search_methods):
        try:
            print(f"\nMethod {i+1}: {method['url']} with {method['params']}")
            response = session.get(method['url'], params=method['params'], timeout=15)
            
            if response.status_code == 200:
                # Look for charity profile URLs in the response
                content = response.text
                
                # Look for profile URLs in HTML
                profile_pattern = r'/charity/charities/[a-f0-9-]+/profile'
                matches = re.findall(profile_pattern, content)
                
                if matches:
                    profile_url = f"https://www.acnc.gov.au{matches[0]}"
                    print(f"  ✓ Found profile URL: {profile_url}")
                    break
                else:
                    print(f"  ✗ No profile URLs found in response")
            else:
                print(f"  ✗ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # If we found a profile URL, try to extract contact info
    if profile_url:
        print(f"\nExtracting contact info from: {profile_url}")
        try:
            profile_response = session.get(profile_url, timeout=30)
            if profile_response.status_code == 200:
                soup = BeautifulSoup(profile_response.content, 'html.parser')
                
                # Extract contact information
                contact_info = {
                    'email': '',
                    'phone': '',
                    'website': ''
                }
                
                # Email - mailto links
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if href.startswith('mailto:') and 'acnc.gov.au' not in href:
                        contact_info['email'] = href.replace('mailto:', '').strip()
                        break
                
                # Phone - Australian patterns in text
                page_text = soup.get_text()
                phone_patterns = [
                    r'(\(?0[2-8]\)?\s*\d{4}\s*\d{4})',
                    r'(\+61\s*[2-8]\s*\d{4}\s*\d{4})',
                    r'(1800\s*\d{3}\s*\d{3})',
                    r'(1300\s*\d{3}\s*\d{3})',
                    r'(13\s*\d{2}\s*\d{2})',
                ]
                
                for pattern in phone_patterns:
                    matches = re.findall(pattern, page_text)
                    if matches:
                        contact_info['phone'] = matches[0].strip()
                        break
                
                # Website - external links
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if (href.startswith('http') and 
                        'acnc.gov.au' not in href and
                        any(ext in href.lower() for ext in ['.org.au', '.edu.au', '.gov.au', '.com.au'])):
                        contact_info['website'] = href
                        break
                
                print(f"Results:")
                print(f"  Email: {contact_info['email'] or 'Not found'}")
                print(f"  Phone: {contact_info['phone'] or 'Not found'}")
                print(f"  Website: {contact_info['website'] or 'Not found'}")
                
            else:
                print(f"  ✗ Profile page HTTP {profile_response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Error extracting contact info: {e}")
    else:
        print(f"  ✗ Could not find profile URL for {charity['name']}")

print("\n" + "="*60)
print("Summary: Need to find working method to locate charity profiles")