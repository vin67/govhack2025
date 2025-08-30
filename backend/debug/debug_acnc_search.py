#!/usr/bin/env python3
"""
Debug script to examine ACNC search results
"""

import requests
from bs4 import BeautifulSoup

# Setup session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-ACNC-DataAgent/1.0)'
})

# Test the charity search page directly
search_url = 'https://www.acnc.gov.au/charity/charities'
params = {
    'search_api_fulltext': 'picton',
    'field_charity_operate_location': 'All',
    'field_charity_size': 'All'
}

print("Testing ACNC search...")
print(f"URL: {search_url}")
print(f"Params: {params}")

try:
    response = session.get(search_url, params=params, timeout=30)
    response.raise_for_status()
    
    print(f"Response status: {response.status_code}")
    print(f"Response URL: {response.url}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Show page title
    title = soup.find('title')
    if title:
        print(f"Page title: {title.get_text()}")
    
    # Show all links
    print("\nAll links on page:")
    link_count = 0
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        link_text = link.get_text().strip()
        if link_text and len(link_text) > 3:
            print(f"  {href} -> {link_text[:60]}")
            link_count += 1
        
        if link_count > 20:  # Limit output
            print("  ... (more links)")
            break
    
    # Look for charity-specific content
    print(f"\nLooking for 'charity' in links...")
    charity_links = 0
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if 'charity' in href.lower():
            link_text = link.get_text().strip()
            print(f"  CHARITY LINK: {href} -> {link_text}")
            charity_links += 1
    
    print(f"\nFound {charity_links} charity-related links")
    
    # Look for picton content
    print(f"\nLooking for 'picton' in page content...")
    page_text = soup.get_text().lower()
    if 'picton' in page_text:
        print("'picton' found in page content")
        # Find context around picton
        import re
        matches = re.finditer(r'.{0,50}picton.{0,50}', page_text, re.IGNORECASE)
        for i, match in enumerate(matches):
            if i >= 5:  # Limit output
                break
            print(f"  Context {i+1}: ...{match.group()}...")
    else:
        print("'picton' NOT found in page content")
    
    # Check if there's a form or if we need to submit something
    forms = soup.find_all('form')
    print(f"\nFound {len(forms)} forms on page")
    for i, form in enumerate(forms):
        if i >= 2:  # Limit output
            break
        action = form.get('action', '')
        method = form.get('method', 'GET').upper()
        print(f"  Form {i+1}: {method} {action}")
        
        # Show form inputs
        inputs = form.find_all(['input', 'select', 'textarea'])
        for inp in inputs[:5]:  # Limit
            inp_type = inp.get('type', inp.name)
            inp_name = inp.get('name', '')
            inp_value = inp.get('value', '')
            print(f"    Input: {inp_type} name={inp_name} value={inp_value}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
