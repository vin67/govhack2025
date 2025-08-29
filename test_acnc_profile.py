#!/usr/bin/env python3
"""
Test ACNC profile URL patterns and scraping
"""

import requests
from bs4 import BeautifulSoup
import re

def test_profile_url():
    """Test known ACNC profile URL pattern"""
    
    # From your screenshot, the URL pattern appears to be:
    # https://www.acnc.gov.au/charity/charities/{UUID}/profile
    
    # Let's try to find the pattern by examining a known charity
    test_charity = "Picton High School P & C Association"
    abn = "43979176197"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-Test/1.0)'
    })
    
    print(f"Testing profile access for: {test_charity}")
    print(f"ABN: {abn}")
    
    # Try different URL patterns
    base_url = "https://www.acnc.gov.au"
    
    # Pattern 1: Search by ABN
    search_url = f"{base_url}/charity/charities?abn={abn}"
    print(f"\n1. Trying search by ABN: {search_url}")
    
    try:
        response = session.get(search_url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for any links that might lead to profiles
            links = soup.find_all('a', href=True)
            profile_links = []
            
            for link in links:
                href = link.get('href')
                if href and ('profile' in href or 'charity/charities' in href):
                    profile_links.append(href)
            
            print(f"   Found {len(profile_links)} potential profile links")
            for link in profile_links[:3]:  # Show first 3
                print(f"     {link}")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    # Pattern 2: Try direct search
    search_url2 = f"{base_url}/charity/charities?q={test_charity.replace(' ', '+')}"
    print(f"\n2. Trying search by name: {search_url2}")
    
    try:
        response = session.get(search_url2, timeout=30)
        print(f"   Status: {response.status_code}")
        
        # Check if page contains JavaScript/Vue content
        content = response.text
        if 'vue-app' in content.lower():
            print("   Page uses Vue.js - dynamic content loading detected")
        
        # Look for any charity data in the HTML
        if test_charity.lower() in content.lower():
            print("   Charity name found in page content")
        else:
            print("   Charity name not found in page content")
    
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_profile_url()