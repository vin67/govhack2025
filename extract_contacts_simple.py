#!/usr/bin/env python3
"""
Simple contact extraction with clear results
"""

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def extract_contacts_from_url(url, name):
    """Extract contact info from a single URL"""
    try:
        print(f"Checking: {name}")
        print(f"URL: {url}")
        
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; ContactBot/1.0)'})
        
        response = session.get(url, timeout=30, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        # Find emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        clean_emails = [e for e in emails if 'noreply' not in e.lower() and 'postmaster' not in e.lower()]
        
        # Find phone numbers
        phone_patterns = [
            r'(\(0[2-8]\)\s*\d{4}\s*\d{4})',
            r'(0[2-8]\s*\d{4}\s*\d{4})',
            r'(\+61\s*[2-8]\s*\d{4}\s*\d{4})',
            r'(1800\s*\d{3}\s*\d{3})',
            r'(1300\s*\d{3}\s*\d{3})',
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        email = clean_emails[0] if clean_emails else ''
        phone = phones[0] if phones else ''
        
        print(f"  Email: {email}")
        print(f"  Phone: {phone}")
        print()
        
        return {'email': email, 'phone': phone}
        
    except Exception as e:
        print(f"  Error: {e}")
        return {'email': '', 'phone': ''}

def main():
    # Test known websites
    test_sites = [
        ('Wollondilly Support & Community Care', 'https://iccare.org.au/'),
        ('Picton High School P&C', 'https://picton-h.schools.nsw.gov.au/'),
        ('Wollondilly Anglican Church', 'https://wollondillyanglican.org'),
        ('Parish of Picton & Wilton Anglican', 'https://pwac.org.au'),
    ]
    
    results = []
    
    for name, url in test_sites:
        contact_info = extract_contacts_from_url(url, name)
        results.append({
            'charity_name': name,
            'website': url,
            'email': contact_info['email'],
            'phone': contact_info['phone']
        })
    
    # Save results
    df = pd.DataFrame(results)
    df.to_csv('verified_charity_contacts.csv', index=False)
    print("Saved verified contacts to: verified_charity_contacts.csv")

if __name__ == "__main__":
    main()