#!/usr/bin/env python3
"""
Scamwatch Threat Intelligence Agent
Extracts scam information from Scamwatch News and Alerts
Looks for phone numbers, emails, websites, and organizations used in scams
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
import re
from urllib.parse import urljoin

class ScamwatchThreatAgent:
    def __init__(self):
        self.base_url = "https://www.scamwatch.gov.au"
        self.news_alerts_url = f"{self.base_url}/about-us/news-and-alerts"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GovHack2025-ScamwatchThreat/1.0)'
        })
    
    def get_news_alert_links(self, limit=10):
        """Stage 1: Get news/alert article links from the main page"""
        print("Scamwatch Threat Intelligence Agent")
        print("=" * 50)
        print(f"Stage 1: Fetching News and Alerts page...")
        print(f"URL: {self.news_alerts_url}")
        
        try:
            response = self.session.get(self.news_alerts_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links on the news page
            article_links = []
            
            # Look for links in common news article structures
            link_selectors = [
                'a[href*="/news-and-alerts/"]',  # News and alerts links
                'a[href*="/scam-alert"]',        # Direct scam alerts
                '.accc-card__title a',           # Card title links
                '.accc-card a',                  # General card links
            ]
            
            for selector in link_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    text = link.get_text().strip()
                    
                    if href and text and len(text) > 10:  # Reasonable title length
                        full_url = urljoin(self.base_url, href)
                        
                        # Filter for scam-related content
                        if any(term in text.lower() for term in 
                              ['scam', 'alert', 'warning', 'fraud', 'threat', 'phishing']):
                            article_links.append({
                                'title': text,
                                'url': full_url
                            })
            
            # Remove duplicates
            unique_links = []
            seen_urls = set()
            
            for link in article_links:
                if link['url'] not in seen_urls and len(unique_links) < limit:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            print(f"Found {len(unique_links)} scam-related articles (limited to {limit})")
            
            for i, link in enumerate(unique_links):
                print(f"{i+1:2}. {link['title']}")
                print(f"     {link['url']}")
            
            return unique_links
            
        except Exception as e:
            print(f"Error fetching news alerts: {e}")
            return []
    
    def extract_threat_intelligence(self, article_title, article_url):
        """Stage 2: Extract threat data from individual scam alert articles"""
        print(f"\n  Analyzing: {article_title[:60]}...")
        
        threat_info = {
            'article_title': article_title,
            'article_url': article_url,
            'scam_type': '',
            'scam_phone_numbers': [],
            'scam_emails': [],
            'scam_websites': [],
            'impersonated_organizations': [],
            'scam_tactics': [],
            'date_reported': '',
            'source': 'Scamwatch'
        }
        
        try:
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            # Identify scam type from title and content
            scam_types = {
                'phone_spoofing': ['phone', 'number', 'spoofed', 'caller id'],
                'email_phishing': ['email', 'phishing', 'inbox', 'message'],
                'job_scam': ['job', 'employment', 'recruitment', 'work'],
                'romance_scam': ['dating', 'romance', 'relationship'],
                'investment_scam': ['investment', 'crypto', 'trading', 'bitcoin'],
                'government_impersonation': ['government', 'ato', 'centrelink', 'medicare'],
                'business_impersonation': ['bank', 'telstra', 'energy', 'utility'],
                'fake_charity': ['charity', 'donation', 'fundraising']
            }
            
            for scam_category, keywords in scam_types.items():
                if any(keyword in page_text.lower() for keyword in keywords):
                    threat_info['scam_type'] = scam_category
                    break
            
            # Extract phone numbers mentioned in scam context
            phone_patterns = [
                r'(\+61\s*[2-8]\s*\d{4}\s*\d{4})',   # +61 X XXXX XXXX
                r'(\(0[2-8]\)\s*\d{4}\s*\d{4})',     # (0X) XXXX XXXX
                r'(0[2-8]\s*\d{4}\s*\d{4})',         # 0X XXXX XXXX
                r'(1800\s*\d{3}\s*\d{3})',           # 1800 XXX XXX
                r'(1300\s*\d{3}\s*\d{3})',           # 1300 XXX XXX
                r'(13\s*\d{2}\s*\d{2})',             # 13 XX XX
            ]
            
            for pattern in phone_patterns:
                matches = re.findall(pattern, page_text)
                for match in matches:
                    clean_number = match.strip()
                    if clean_number not in threat_info['scam_phone_numbers']:
                        threat_info['scam_phone_numbers'].append(clean_number)
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, page_text)
            for email in emails:
                # Filter out legitimate government/organization emails
                if not any(domain in email.lower() for domain in 
                          ['scamwatch.gov.au', 'accc.gov.au', 'example.com']):
                    if email not in threat_info['scam_emails']:
                        threat_info['scam_emails'].append(email)
            
            # Extract websites/domains mentioned as scam sites
            url_pattern = r'https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            urls = re.findall(url_pattern, page_text)
            for url in urls:
                # Filter out legitimate sites
                if not any(domain in url.lower() for domain in 
                          ['scamwatch.gov.au', 'accc.gov.au', 'gov.au']):
                    if url not in threat_info['scam_websites']:
                        threat_info['scam_websites'].append(url)
            
            # Extract impersonated organizations
            org_keywords = [
                'impersonate', 'impersonating', 'pretend', 'pose as', 'claim to be',
                'represent', 'from the', 'calling from'
            ]
            
            organizations = [
                'ACCC', 'ATO', 'Centrelink', 'Medicare', 'Police', 'Bank',
                'Telstra', 'Optus', 'Energy Australia', 'Origin', 'Netflix',
                'Amazon', 'eBay', 'PayPal', 'Commonwealth Bank', 'ANZ',
                'Westpac', 'NAB', 'Government', 'Tax Office'
            ]
            
            for org in organizations:
                if org.lower() in page_text.lower():
                    # Check if mentioned in scam context
                    for keyword in org_keywords:
                        if keyword in page_text.lower() and org.lower() in page_text.lower():
                            if org not in threat_info['impersonated_organizations']:
                                threat_info['impersonated_organizations'].append(org)
                            break
            
            # Extract date from article
            date_patterns = [
                r'(\d{1,2}\s+\w+\s+\d{4})',  # "29 August 2025"
                r'(\w+\s+\d{1,2},?\s+\d{4})', # "August 29, 2025"
                r'(\d{4}-\d{2}-\d{2})'        # "2025-08-29"
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    threat_info['date_reported'] = matches[0]
                    break
            
            # Extract common scam tactics
            tactics = {
                'urgency': ['urgent', 'immediate', 'act now', 'expires'],
                'fear': ['suspended', 'blocked', 'arrest', 'penalty'],
                'authority': ['government', 'official', 'authority', 'legal'],
                'greed': ['money', 'profit', 'investment', 'opportunity'],
                'curiosity': ['click here', 'verify', 'confirm', 'update']
            }
            
            for tactic_name, keywords in tactics.items():
                if any(keyword in page_text.lower() for keyword in keywords):
                    threat_info['scam_tactics'].append(tactic_name)
            
            print(f"    Scam Type: {threat_info['scam_type']}")
            print(f"    Phone Numbers: {len(threat_info['scam_phone_numbers'])}")
            print(f"    Emails: {len(threat_info['scam_emails'])}")
            print(f"    Websites: {len(threat_info['scam_websites'])}")
            print(f"    Impersonated Orgs: {len(threat_info['impersonated_organizations'])}")
            
        except Exception as e:
            print(f"    Error extracting threat intelligence: {e}")
        
        return threat_info
    
    def scrape_threat_intelligence(self, limit=10):
        """Complete threat intelligence scraping process"""
        # Stage 1: Get article links
        article_links = self.get_news_alert_links(limit)
        
        if not article_links:
            print("No scam articles found")
            return []
        
        print(f"\nStage 2: Extracting threat intelligence from {len(article_links)} articles...")
        
        # Stage 2: Extract threat data from each article
        threat_data = []
        
        for i, link in enumerate(article_links):
            print(f"\nProcessing {i+1}/{len(article_links)}")
            
            threat_info = self.extract_threat_intelligence(link['title'], link['url'])
            threat_data.append(threat_info)
            
            # Rate limiting
            time.sleep(2)
        
        return threat_data
    
    def save_threat_data(self, threat_data, filename='scamwatch_threats.csv'):
        """Save threat intelligence to CSV"""
        if not threat_data:
            print("No threat data to save")
            return
        
        # Flatten the data for CSV
        flattened_data = []
        
        for threat in threat_data:
            base_record = {
                'article_title': threat['article_title'],
                'article_url': threat['article_url'],
                'scam_type': threat['scam_type'],
                'date_reported': threat['date_reported'],
                'scam_tactics': ', '.join(threat['scam_tactics']),
                'impersonated_organizations': ', '.join(threat['impersonated_organizations']),
                'source': threat['source']
            }
            
            # Create separate records for each contact method
            contact_types = [
                ('phone', threat['scam_phone_numbers']),
                ('email', threat['scam_emails']),
                ('website', threat['scam_websites'])
            ]
            
            has_contacts = False
            for contact_type, contacts in contact_types:
                for contact in contacts:
                    record = base_record.copy()
                    record['threat_type'] = contact_type
                    record['threat_value'] = contact
                    flattened_data.append(record)
                    has_contacts = True
            
            # If no specific contacts found, still save the general threat info
            if not has_contacts:
                record = base_record.copy()
                record['threat_type'] = 'general'
                record['threat_value'] = ''
                flattened_data.append(record)
        
        # Save to CSV
        if flattened_data:
            fieldnames = [
                'article_title', 'scam_type', 'threat_type', 'threat_value',
                'date_reported', 'scam_tactics', 'impersonated_organizations',
                'article_url', 'source'
            ]
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened_data)
            
            print(f"\nSaved {len(flattened_data)} threat intelligence records to {filename}")
            
            # Summary statistics
            threat_types = {}
            for record in flattened_data:
                ttype = record['threat_type']
                threat_types[ttype] = threat_types.get(ttype, 0) + 1
            
            print(f"\nThreat Intelligence Summary:")
            print(f"  Total articles analyzed: {len(threat_data)}")
            print(f"  Total threat indicators: {len(flattened_data)}")
            for ttype, count in threat_types.items():
                print(f"  {ttype.title()}: {count}")

def main():
    """Main execution function"""
    agent = ScamwatchThreatAgent()
    
    # Extract threat intelligence from 10 articles
    threat_data = agent.scrape_threat_intelligence(limit=10)
    
    if threat_data:
        agent.save_threat_data(threat_data)
        
        print(f"\nSample Threat Intelligence:")
        for i, threat in enumerate(threat_data[:3]):
            print(f"\n{i+1}. {threat['article_title'][:50]}...")
            print(f"   Type: {threat['scam_type']}")
            if threat['scam_phone_numbers']:
                print(f"   Scam Numbers: {', '.join(threat['scam_phone_numbers'][:3])}")
            if threat['scam_emails']:
                print(f"   Scam Emails: {', '.join(threat['scam_emails'][:3])}")
            if threat['impersonated_organizations']:
                print(f"   Impersonates: {', '.join(threat['impersonated_organizations'][:3])}")
    else:
        print("No threat intelligence collected")

if __name__ == "__main__":
    main()