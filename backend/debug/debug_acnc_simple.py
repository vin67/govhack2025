#!/usr/bin/env python3
"""
Simple ACNC Debug - Just load the search page and see its structure
"""

import requests
from bs4 import BeautifulSoup

def inspect_acnc_search_page():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    print("🔍 Inspecting ACNC Search Page Structure")
    print("=" * 50)
    
    try:
        # Load the charity search page
        url = 'https://www.acnc.gov.au/charity/search'
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Successfully loaded: {url}")
        print(f"Status code: {response.status_code}")
        print()
        
        # Look for all forms and their inputs
        print("📝 FORMS FOUND:")
        forms = soup.find_all('form')
        
        for i, form in enumerate(forms, 1):
            print(f"\nForm {i}:")
            print(f"  Action: {form.get('action', 'None')}")
            print(f"  Method: {form.get('method', 'GET').upper()}")
            
            # Get all input fields
            inputs = form.find_all(['input', 'select', 'textarea'])
            print(f"  Fields ({len(inputs)}):")
            
            for inp in inputs:
                field_type = inp.get('type', inp.name)
                field_name = inp.get('name', 'unnamed')
                field_value = inp.get('value', '')
                placeholder = inp.get('placeholder', '')
                
                if field_type != 'hidden':
                    print(f"    - {field_name}: {field_type}")
                    if placeholder:
                        print(f"      placeholder: {placeholder}")
                    if field_value:
                        print(f"      default: {field_value}")
        
        # Look for any existing search results or examples
        print("\n🔍 LOOKING FOR SEARCH RESULT STRUCTURE:")
        result_links = soup.find_all('a', href=True)
        charity_links = [link for link in result_links if 'charity/charities' in link.get('href', '')]
        
        if charity_links:
            print(f"Found {len(charity_links)} charity profile links:")
            for link in charity_links[:3]:  # Show first 3
                print(f"  - {link.get_text()[:60]}...")
                print(f"    {link.get('href')}")
        else:
            print("No charity profile links found on search page")
            
        # Look for JavaScript that might handle search
        print("\n💻 JAVASCRIPT SEARCH HANDLING:")
        scripts = soup.find_all('script')
        search_scripts = [s for s in scripts if s.string and ('search' in s.string.lower() or 'charity' in s.string.lower())]
        
        if search_scripts:
            print(f"Found {len(search_scripts)} search-related scripts")
            for script in search_scripts[:1]:  # Show first one
                content = script.string[:200] + '...' if len(script.string) > 200 else script.string
                print(f"  Script preview: {content}")
        else:
            print("No obvious search-related JavaScript found")
            
    except Exception as e:
        print(f"❌ Error inspecting search page: {e}")

if __name__ == "__main__":
    inspect_acnc_search_page()