#!/usr/bin/env python3
"""Simple debug to find the table structure"""

import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-ACNC-DataAgent/1.0)'
})

# Use the exact URL from the screenshot
search_url = 'https://www.acnc.gov.au/charity/charities'
params = {'location': 'picton'}

print(f"Testing: {search_url} with params: {params}")

try:
    response = session.get(search_url, params=params, timeout=30)
    response.raise_for_status()
    
    print(f"Response status: {response.status_code}")
    
    # Get the raw HTML and search for key patterns
    html_content = response.text
    
    # Look for the patterns you mentioned
    if 'results mt-4' in html_content:
        print("✓ Found 'results mt-4' pattern in HTML!")
        # Find the position and show context
        pos = html_content.find('results mt-4')
        context = html_content[max(0, pos-200):pos+800]
        print("Context around 'results mt-4':")
        print(context)
    else:
        print("✗ 'results mt-4' pattern not found")
    
    # Look for data-v-5f6e0f24 pattern from screenshot
    if 'data-v-5f6e0f24' in html_content:
        print("\n✓ Found 'data-v-5f6e0f24' pattern in HTML!")
        pos = html_content.find('data-v-5f6e0f24')
        context = html_content[max(0, pos-100):pos+500]
        print("Context around 'data-v-5f6e0f24':")
        print(context)
    else:
        print("\n✗ 'data-v-5f6e0f24' pattern not found")
    
    # Look for charity profile URLs
    if '/charity/charities/' in html_content:
        print("\n✓ Found charity profile URL patterns!")
        import re
        charity_urls = re.findall(r'/charity/charities/[^"\'>\s]+', html_content)
        print(f"Found {len(charity_urls)} charity URL patterns:")
        for url in charity_urls[:5]:
            print(f"  {url}")
    else:
        print("\n✗ No charity profile URLs found")
    
    # Look for table-related HTML structures
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Search for divs with classes that might contain the table
    potential_containers = soup.find_all('div', class_=True)
    results_divs = []
    
    for div in potential_containers:
        classes = div.get('class', [])
        class_str = ' '.join(classes) if isinstance(classes, list) else str(classes)
        if 'results' in class_str.lower() or 'table' in class_str.lower():
            results_divs.append((div, class_str))
    
    print(f"\nFound {len(results_divs)} divs with 'results' or 'table' in class")
    for div, class_str in results_divs[:3]:
        print(f"  Classes: {class_str}")
        print(f"  Content preview: {str(div)[:200]}...")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()