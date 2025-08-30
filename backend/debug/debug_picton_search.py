#!/usr/bin/env python3
"""Debug the exact Picton charity search URL"""

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
    print(f"Final URL: {response.url}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check page title
    title = soup.find('title')
    print(f"Page title: {title.get_text() if title else 'No title'}")
    
    # Look for tables
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables")
    
    # Look for any tr elements with data-v attributes
    data_rows = soup.find_all('tr', attrs=lambda x: x and any('data-v-' in str(k) for k in x.keys()))
    print(f"Found {len(data_rows)} rows with data-v attributes")
    
    # Look for any links containing charity/charities
    charity_links = []
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if '/charity/charities/' in href:
            charity_links.append((href, link.get_text().strip()))
    
    print(f"Found {len(charity_links)} charity profile links:")
    for href, text in charity_links[:5]:  # Show first 5
        print(f"  {href} -> {text}")
    
    # Look for specific text indicators
    page_text = soup.get_text().lower()
    picton_count = page_text.count('picton')
    print(f"'picton' appears {picton_count} times in page text")
    
    # Check if there's any JavaScript that might load content
    scripts = soup.find_all('script')
    print(f"Found {len(scripts)} script tags")
    
    # Look for any Vue.js or dynamic content indicators
    vue_elements = soup.find_all(attrs=lambda x: x and any('vue' in str(k).lower() or 'vue' in str(v).lower() for k, v in x.items() if isinstance(v, (str, list))))
    print(f"Found {len(vue_elements)} elements with Vue indicators")
    
    # Look for the specific pattern you mentioned - "results mt-4"
    results_sections = soup.find_all(attrs=lambda x: x and 'results' in str(x).get('class', []))
    print(f"Found {len(results_sections)} elements with 'results' class")
    
    mt4_sections = soup.find_all(attrs=lambda x: x and 'mt-4' in str(x).get('class', []))  
    print(f"Found {len(mt4_sections)} elements with 'mt-4' class")
    
    # Look for combination "results mt-4"
    results_mt4 = soup.find_all(attrs=lambda x: x and isinstance(x.get('class'), list) and 'results' in x.get('class') and 'mt-4' in x.get('class'))
    print(f"Found {len(results_mt4)} elements with both 'results' and 'mt-4' classes")
    
    # Show the raw HTML content to see the structure
    print(f"\nRaw HTML content (first 3000 chars):")
    print(str(soup)[:3000])
    
    # Look for any div or section that might contain the table
    for element in soup.find_all(['div', 'section']):
        classes = element.get('class', [])
        if isinstance(classes, list) and ('results' in classes or 'mt-4' in classes):
            print(f"\nFound element with relevant classes: {classes}")
            print(f"Content preview: {str(element)[:500]}")
    
    # Look for table-like structures even if not in <table> tags
    table_like = soup.find_all(attrs=lambda x: x and 'table' in str(x).get('class', []))
    print(f"Found {len(table_like)} elements with 'table' in class")
    
    for element in table_like:
        print(f"Table-like element: {element.name} with classes {element.get('class', [])}")
        print(f"Content: {str(element)[:300]}...")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()