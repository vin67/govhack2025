#!/usr/bin/env python3
"""Try to find ACNC API endpoints"""

import requests
import json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-ACNC-DataAgent/1.0)'
})

# Try possible API endpoints based on common patterns
api_endpoints = [
    'https://www.acnc.gov.au/api/charity/search',
    'https://www.acnc.gov.au/api/charities',
    'https://www.acnc.gov.au/api/v1/charities', 
    'https://api.acnc.gov.au/charities',
    'https://api.acnc.gov.au/v1/charities',
    'https://www.acnc.gov.au/charity/api/search',
    'https://www.acnc.gov.au/search/api',
]

params_to_try = [
    {'location': 'picton'},
    {'q': 'picton'},
    {'search': 'picton'},
    {'keyword': 'picton'},
    {'location': 'picton', 'format': 'json'},
]

print("Trying potential API endpoints...")

for endpoint in api_endpoints:
    for params in params_to_try:
        try:
            print(f"\nTrying: {endpoint} with {params}")
            
            response = session.get(endpoint, params=params, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                print(f"  Content-Type: {content_type}")
                
                if 'json' in content_type:
                    try:
                        data = response.json()
                        print(f"  JSON response with {len(data)} items" if isinstance(data, list) else f"  JSON response: {list(data.keys()) if isinstance(data, dict) else 'other'}")
                        
                        # If we got data, show a sample
                        if isinstance(data, list) and data:
                            print(f"  Sample item: {data[0]}")
                        elif isinstance(data, dict):
                            print(f"  Sample keys: {list(data.keys())[:5]}")
                    except:
                        print(f"  Not valid JSON")
                else:
                    print(f"  HTML/Text response (first 200 chars): {response.text[:200]}")
                    
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
            
# Also try looking for AJAX endpoints by examining the JavaScript
print(f"\n" + "="*50)
print("Checking main page JavaScript for API calls...")

try:
    main_page = session.get('https://www.acnc.gov.au/charity/charities?location=picton')
    html_content = main_page.text
    
    # Look for common API call patterns in JavaScript
    import re
    
    # Look for URLs in JavaScript that might be API calls
    url_patterns = [
        r'["\']https?://[^"\']*api[^"\']*["\']',
        r'["\'][./]*api[^"\']*["\']',
        r'fetch\(["\']([^"\']+)["\']',
        r'axios\.get\(["\']([^"\']+)["\']',
        r'\.get\(["\']([^"\']+)["\']',
        r'url:\s*["\']([^"\']+)["\']',
    ]
    
    found_apis = set()
    for pattern in url_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        found_apis.update(matches)
    
    print(f"Found {len(found_apis)} potential API URLs in JavaScript:")
    for api_url in sorted(found_apis):
        if 'api' in api_url.lower() or 'search' in api_url.lower():
            print(f"  {api_url}")
            
except Exception as e:
    print(f"Error checking JavaScript: {e}")