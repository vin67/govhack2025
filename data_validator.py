#!/usr/bin/env python3
"""
Data Validation and Cross-Reference System
Combines all agent data to identify legitimate vs threat contacts
"""

import pandas as pd
import csv
import json
from pathlib import Path
from collections import defaultdict

class DataValidator:
    def __init__(self):
        self.legitimate_data = {}
        self.threat_data = {}
        self.validation_results = {
            'verified_legitimate': [],
            'potential_threats': [],
            'cross_references': [],
            'statistics': {}
        }
        
    def load_all_datasets(self):
        """Load all agent datasets"""
        print("Data Validation and Cross-Reference System")
        print("=" * 50)
        print("Loading datasets from all agents...")
        
        # Load legitimate government/charity data
        datasets = [
            ('government_services.csv', 'federal_services'),
            ('acnc_charity_data.csv', 'charity_register'),
            ('nsw_services.csv', 'nsw_services'),
            ('nsw_hospitals.csv', 'nsw_hospitals')
        ]
        
        for filename, source_type in datasets:
            filepath = Path(filename)
            if filepath.exists():
                print(f"  ✓ Loading {filename}")
                df = pd.read_csv(filepath)
                self.legitimate_data[source_type] = df
                print(f"    Records: {len(df)}")
            else:
                print(f"  ✗ Missing {filename}")
        
        # Load threat intelligence
        threat_file = Path('scamwatch_threats.csv')
        if threat_file.exists():
            print(f"  ✓ Loading threat intelligence")
            df = pd.read_csv(threat_file)
            self.threat_data['scamwatch'] = df
            print(f"    Threat indicators: {len(df)}")
        else:
            print(f"  ✗ Missing threat data")
    
    def extract_all_contacts(self):
        """Extract all phone numbers and emails from legitimate sources"""
        legitimate_contacts = {
            'phones': set(),
            'emails': set(),
            'websites': set()
        }
        
        print(f"\nExtracting contact information from legitimate sources...")
        
        # Process each legitimate dataset
        for source_type, df in self.legitimate_data.items():
            print(f"  Processing {source_type}...")
            
            # Look for phone number columns
            phone_cols = [col for col in df.columns if 
                         any(term in col.lower() for term in ['phone', 'tel', 'contact', 'number'])]
            
            # Look for email columns
            email_cols = [col for col in df.columns if 
                         any(term in col.lower() for term in ['email', 'mail'])]
            
            # Look for website columns
            website_cols = [col for col in df.columns if 
                           any(term in col.lower() for term in ['website', 'web', 'url', 'link'])]
            
            # Extract phone numbers
            for col in phone_cols:
                phones = df[col].dropna().astype(str)
                for phone in phones:
                    cleaned_phone = self.clean_phone_number(phone)
                    if cleaned_phone and len(cleaned_phone) >= 8:
                        legitimate_contacts['phones'].add(cleaned_phone)
            
            # Extract emails
            for col in email_cols:
                emails = df[col].dropna().astype(str)
                for email in emails:
                    if '@' in email and '.' in email:
                        legitimate_contacts['emails'].add(email.strip().lower())
            
            # Extract websites
            for col in website_cols:
                websites = df[col].dropna().astype(str)
                for website in websites:
                    if any(proto in website for proto in ['http', 'www', '.com', '.gov', '.org']):
                        legitimate_contacts['websites'].add(website.strip().lower())
        
        print(f"    Legitimate phones: {len(legitimate_contacts['phones'])}")
        print(f"    Legitimate emails: {len(legitimate_contacts['emails'])}")
        print(f"    Legitimate websites: {len(legitimate_contacts['websites'])}")
        
        return legitimate_contacts
    
    def extract_threat_indicators(self):
        """Extract threat indicators from scam data"""
        threat_indicators = {
            'phones': set(),
            'emails': set(),
            'websites': set(),
            'impersonated_orgs': set()
        }
        
        print(f"\nExtracting threat indicators...")
        
        if 'scamwatch' in self.threat_data:
            df = self.threat_data['scamwatch']
            
            # Extract threat phone numbers
            threat_phones = df[df['threat_type'] == 'phone']['threat_value'].dropna()
            for phone in threat_phones:
                cleaned_phone = self.clean_phone_number(str(phone))
                if cleaned_phone:
                    threat_indicators['phones'].add(cleaned_phone)
            
            # Extract threat emails
            threat_emails = df[df['threat_type'] == 'email']['threat_value'].dropna()
            for email in threat_emails:
                if '@' in str(email):
                    threat_indicators['emails'].add(str(email).strip().lower())
            
            # Extract threat websites
            threat_websites = df[df['threat_type'] == 'website']['threat_value'].dropna()
            for website in threat_websites:
                threat_indicators['websites'].add(str(website).strip().lower())
            
            # Extract impersonated organizations
            impersonated = df['impersonated_organizations'].dropna()
            for orgs in impersonated:
                if pd.notna(orgs) and str(orgs).strip():
                    for org in str(orgs).split(','):
                        threat_indicators['impersonated_orgs'].add(org.strip())
        
        print(f"    Threat phones: {len(threat_indicators['phones'])}")
        print(f"    Threat emails: {len(threat_indicators['emails'])}")
        print(f"    Threat websites: {len(threat_indicators['websites'])}")
        print(f"    Impersonated orgs: {len(threat_indicators['impersonated_orgs'])}")
        
        return threat_indicators
    
    def cross_reference_data(self, legitimate_contacts, threat_indicators):
        """Cross-reference legitimate vs threat data"""
        print(f"\nCross-referencing legitimate contacts against threat indicators...")
        
        results = {
            'compromised_phones': [],
            'compromised_emails': [],
            'compromised_websites': [],
            'safe_contacts': {
                'phones': legitimate_contacts['phones'] - threat_indicators['phones'],
                'emails': legitimate_contacts['emails'] - threat_indicators['emails'],
                'websites': legitimate_contacts['websites'] - threat_indicators['websites']
            }
        }
        
        # Find compromised contacts
        compromised_phones = legitimate_contacts['phones'].intersection(threat_indicators['phones'])
        compromised_emails = legitimate_contacts['emails'].intersection(threat_indicators['emails'])
        compromised_websites = legitimate_contacts['websites'].intersection(threat_indicators['websites'])
        
        results['compromised_phones'] = list(compromised_phones)
        results['compromised_emails'] = list(compromised_emails)
        results['compromised_websites'] = list(compromised_websites)
        
        # Statistics
        print(f"  🚨 COMPROMISED CONTACTS FOUND:")
        print(f"    Compromised phones: {len(compromised_phones)}")
        print(f"    Compromised emails: {len(compromised_emails)}")
        print(f"    Compromised websites: {len(compromised_websites)}")
        
        print(f"  ✅ VERIFIED SAFE CONTACTS:")
        print(f"    Safe phones: {len(results['safe_contacts']['phones'])}")
        print(f"    Safe emails: {len(results['safe_contacts']['emails'])}")
        print(f"    Safe websites: {len(results['safe_contacts']['websites'])}")
        
        if compromised_phones:
            print(f"\n  ⚠️  COMPROMISED PHONE NUMBERS:")
            for phone in compromised_phones:
                print(f"    {phone}")
        
        return results
    
    def clean_phone_number(self, phone_text):
        """Clean phone number for comparison"""
        import re
        
        if not phone_text or str(phone_text).lower() in ['nan', 'none', '']:
            return ""
        
        phone_clean = str(phone_text).strip()
        phone_clean = re.sub(r'[^\d+()]', ' ', phone_clean)
        phone_clean = re.sub(r'\s+', ' ', phone_clean)
        
        return phone_clean.strip()
    
    def save_validation_results(self, cross_ref_results, filename='validation_report.json'):
        """Save validation results to JSON"""
        report = {
            'validation_timestamp': pd.Timestamp.now().isoformat(),
            'data_sources': {
                'legitimate_sources': list(self.legitimate_data.keys()),
                'threat_sources': list(self.threat_data.keys())
            },
            'statistics': {
                'total_legitimate_phones': len(cross_ref_results['safe_contacts']['phones']) + len(cross_ref_results['compromised_phones']),
                'total_legitimate_emails': len(cross_ref_results['safe_contacts']['emails']) + len(cross_ref_results['compromised_emails']),
                'total_legitimate_websites': len(cross_ref_results['safe_contacts']['websites']) + len(cross_ref_results['compromised_websites']),
                'compromised_phones': len(cross_ref_results['compromised_phones']),
                'compromised_emails': len(cross_ref_results['compromised_emails']),
                'compromised_websites': len(cross_ref_results['compromised_websites']),
                'safe_phones': len(cross_ref_results['safe_contacts']['phones']),
                'safe_emails': len(cross_ref_results['safe_contacts']['emails']),
                'safe_websites': len(cross_ref_results['safe_contacts']['websites'])
            },
            'compromised_contacts': {
                'phones': cross_ref_results['compromised_phones'],
                'emails': cross_ref_results['compromised_emails'],
                'websites': cross_ref_results['compromised_websites']
            },
            'verified_safe_sample': {
                'phones': list(cross_ref_results['safe_contacts']['phones'])[:10],
                'emails': list(cross_ref_results['safe_contacts']['emails'])[:10],
                'websites': list(cross_ref_results['safe_contacts']['websites'])[:10]
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nValidation report saved to {filename}")
        return report
    
    def run_full_validation(self):
        """Run complete validation process"""
        # Load all datasets
        self.load_all_datasets()
        
        if not self.legitimate_data and not self.threat_data:
            print("No data available for validation")
            return None
        
        # Extract contacts
        legitimate_contacts = self.extract_all_contacts()
        threat_indicators = self.extract_threat_indicators()
        
        # Cross-reference
        cross_ref_results = self.cross_reference_data(legitimate_contacts, threat_indicators)
        
        # Save results
        report = self.save_validation_results(cross_ref_results)
        
        return report

def main():
    """Main execution function"""
    validator = DataValidator()
    report = validator.run_full_validation()
    
    if report:
        print(f"\n" + "=" * 50)
        print(f"VALIDATION SUMMARY")
        print(f"=" * 50)
        stats = report['statistics']
        
        print(f"Total legitimate contacts analyzed:")
        print(f"  📞 Phone numbers: {stats['total_legitimate_phones']}")
        print(f"  📧 Email addresses: {stats['total_legitimate_emails']}")
        print(f"  🌐 Websites: {stats['total_legitimate_websites']}")
        
        print(f"\nThreat analysis results:")
        print(f"  🚨 Compromised phones: {stats['compromised_phones']}")
        print(f"  🚨 Compromised emails: {stats['compromised_emails']}")
        print(f"  🚨 Compromised websites: {stats['compromised_websites']}")
        
        print(f"  ✅ Verified safe phones: {stats['safe_phones']}")
        print(f"  ✅ Verified safe emails: {stats['safe_emails']}")
        print(f"  ✅ Verified safe websites: {stats['safe_websites']}")
        
        # Calculate safety percentages
        if stats['total_legitimate_phones'] > 0:
            safety_rate = (stats['safe_phones'] / stats['total_legitimate_phones']) * 100
            print(f"\nPhone number safety rate: {safety_rate:.1f}%")

if __name__ == "__main__":
    main()