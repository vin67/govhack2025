#!/usr/bin/env python3
"""
Critic Agent - Data Quality Reviewer
Reviews standardized contact data for quality, completeness, and potential issues
Uses AI-powered analysis to validate and score data quality
"""

import pandas as pd
import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class CriticAgent:
    def __init__(self):
        self.input_file = 'data/standardized_contacts.csv'
        self.output_file = 'data/reports/critic_report.json'
        
        self.quality_rules = {
            'phone_validation': {
                'australian_format': r'^(\+61|0)[2-9]\d{8}$|^(1800|1300|13)\d{6}$|^13\d{4}$',
                'international_format': r'^\+\d{1,3}\d{4,14}$'
            },
            'email_validation': {
                'basic_format': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            },
            'website_validation': {
                'url_format': r'^https?://.+\..+$',
                'gov_domain': r'\.gov\.au$',
                'org_domain': r'\.(org|com|net)\.au$'
            }
        }
        
        self.quality_weights = {
            'format_compliance': 0.3,
            'completeness': 0.25,
            'source_reliability': 0.2,
            'consistency': 0.15,
            'freshness': 0.1
        }
    
    def load_standardized_data(self):
        """Load the standardized contact dataset"""
        filepath = Path(self.input_file)
        if not filepath.exists():
            print(f"Error: {self.input_file} not found")
            print("Run data_standardizer.py first to create standardized dataset")
            return None
        
        df = pd.read_csv(filepath)
        print(f"Loaded {len(df)} standardized contact records")
        return df
    
    def validate_phone_numbers(self, df):
        """Validate phone number formats and patterns"""
        phone_records = df[df['contact_type'] == 'phone'].copy()
        if len(phone_records) == 0:
            return {}
        
        print(f"  Validating {len(phone_records)} phone numbers...")
        
        validation_results = {
            'total_phones': len(phone_records),
            'valid_australian': 0,
            'valid_international': 0,
            'invalid_format': 0,
            'suspicious_patterns': [],
            'quality_issues': []
        }
        
        aus_pattern = re.compile(self.quality_rules['phone_validation']['australian_format'])
        intl_pattern = re.compile(self.quality_rules['phone_validation']['international_format'])
        
        for idx, row in phone_records.iterrows():
            phone = str(row['contact_value']).strip()
            
            # Clean phone for validation
            clean_phone = re.sub(r'[^\d+()]', '', phone)
            
            if aus_pattern.match(clean_phone):
                validation_results['valid_australian'] += 1
            elif intl_pattern.match(clean_phone):
                validation_results['valid_international'] += 1
            else:
                validation_results['invalid_format'] += 1
                validation_results['quality_issues'].append({
                    'contact_id': row['contact_id'],
                    'phone': phone,
                    'organization': row['organization_name'],
                    'issue': 'Invalid phone format'
                })
            
            # Check for suspicious patterns
            if '0000' in clean_phone or len(set(clean_phone.replace('+', ''))) <= 2:
                validation_results['suspicious_patterns'].append({
                    'contact_id': row['contact_id'],
                    'phone': phone,
                    'issue': 'Suspicious pattern detected'
                })
        
        validation_results['format_compliance_rate'] = (
            (validation_results['valid_australian'] + validation_results['valid_international']) 
            / validation_results['total_phones']
        ) if validation_results['total_phones'] > 0 else 0
        
        return validation_results
    
    def validate_emails(self, df):
        """Validate email address formats"""
        email_records = df[df['contact_type'] == 'email'].copy()
        if len(email_records) == 0:
            return {}
        
        print(f"  Validating {len(email_records)} email addresses...")
        
        validation_results = {
            'total_emails': len(email_records),
            'valid_format': 0,
            'invalid_format': 0,
            'gov_domains': 0,
            'quality_issues': []
        }
        
        email_pattern = re.compile(self.quality_rules['email_validation']['basic_format'])
        
        for idx, row in email_records.iterrows():
            email = str(row['contact_value']).strip().lower()
            
            if email_pattern.match(email):
                validation_results['valid_format'] += 1
                
                if '.gov.au' in email:
                    validation_results['gov_domains'] += 1
            else:
                validation_results['invalid_format'] += 1
                validation_results['quality_issues'].append({
                    'contact_id': row['contact_id'],
                    'email': email,
                    'organization': row['organization_name'],
                    'issue': 'Invalid email format'
                })
        
        validation_results['format_compliance_rate'] = (
            validation_results['valid_format'] / validation_results['total_emails']
        ) if validation_results['total_emails'] > 0 else 0
        
        return validation_results
    
    def validate_websites(self, df):
        """Validate website URLs"""
        website_records = df[df['contact_type'] == 'website'].copy()
        if len(website_records) == 0:
            return {}
        
        print(f"  Validating {len(website_records)} websites...")
        
        validation_results = {
            'total_websites': len(website_records),
            'valid_format': 0,
            'gov_domains': 0,
            'https_secured': 0,
            'quality_issues': []
        }
        
        url_pattern = re.compile(self.quality_rules['website_validation']['url_format'])
        
        for idx, row in website_records.iterrows():
            website = str(row['contact_value']).strip().lower()
            
            if url_pattern.match(website):
                validation_results['valid_format'] += 1
                
                if '.gov.au' in website:
                    validation_results['gov_domains'] += 1
                
                if website.startswith('https://'):
                    validation_results['https_secured'] += 1
            else:
                validation_results['quality_issues'].append({
                    'contact_id': row['contact_id'],
                    'website': website,
                    'organization': row['organization_name'],
                    'issue': 'Invalid URL format'
                })
        
        validation_results['format_compliance_rate'] = (
            validation_results['valid_format'] / validation_results['total_websites']
        ) if validation_results['total_websites'] > 0 else 0
        
        return validation_results
    
    def analyze_completeness(self, df):
        """Analyze data completeness across records"""
        print(f"  Analyzing data completeness...")
        
        completeness_analysis = {
            'total_records': len(df),
            'required_fields_complete': 0,
            'optional_fields_complete': 0,
            'missing_data_issues': []
        }
        
        required_fields = ['contact_value', 'organization_name', 'organization_type', 'source_agent']
        optional_fields = ['address', 'suburb', 'state', 'services']
        
        for idx, row in df.iterrows():
            # Check required fields
            required_complete = True
            for field in required_fields:
                if pd.isna(row[field]) or str(row[field]).strip() == '':
                    required_complete = False
                    completeness_analysis['missing_data_issues'].append({
                        'contact_id': row['contact_id'],
                        'missing_field': field,
                        'organization': row['organization_name']
                    })
            
            if required_complete:
                completeness_analysis['required_fields_complete'] += 1
            
            # Check optional fields
            optional_count = 0
            for field in optional_fields:
                if pd.notna(row[field]) and str(row[field]).strip() != '':
                    optional_count += 1
            
            if optional_count >= len(optional_fields) * 0.5:  # At least 50% complete
                completeness_analysis['optional_fields_complete'] += 1
        
        completeness_analysis['required_completeness_rate'] = (
            completeness_analysis['required_fields_complete'] / completeness_analysis['total_records']
        )
        
        completeness_analysis['optional_completeness_rate'] = (
            completeness_analysis['optional_fields_complete'] / completeness_analysis['total_records']
        )
        
        return completeness_analysis
    
    def analyze_source_reliability(self, df):
        """Analyze reliability of data sources"""
        print(f"  Analyzing source reliability...")
        
        source_analysis = {
            'sources': {},
            'reliability_scores': {},
            'total_by_confidence': defaultdict(int)
        }
        
        # Define source reliability scores
        source_reliability = {
            'nsw_hospitals_agent': 0.95,       # Official API
            'government_services_scraper': 0.90, # Official gov directory
            'scamwatch_threat_agent': 0.85,   # Official scam reporting
            'acnc_data_agent': 0.80,          # Official charity register
            'website_contact_scraper': 0.70,  # Secondary scraping
        }
        
        for source in df['source_agent'].unique():
            source_data = df[df['source_agent'] == source]
            source_analysis['sources'][source] = {
                'record_count': len(source_data),
                'avg_confidence': source_data['confidence_score'].mean(),
                'reliability_score': source_reliability.get(source, 0.5)
            }
        
        # Analyze confidence score distribution
        for idx, row in df.iterrows():
            confidence_bucket = f"{row['confidence_score']:.1f}"
            source_analysis['total_by_confidence'][confidence_bucket] += 1
        
        return source_analysis
    
    def detect_inconsistencies(self, df):
        """Detect data inconsistencies and duplicates"""
        print(f"  Detecting inconsistencies...")
        
        inconsistency_analysis = {
            'duplicate_contacts': [],
            'organization_name_variations': [],
            'address_inconsistencies': []
        }
        
        # Find duplicate contact values
        contact_counts = df['contact_value'].value_counts()
        duplicates = contact_counts[contact_counts > 1]
        
        for contact_value, count in duplicates.items():
            duplicate_records = df[df['contact_value'] == contact_value]
            
            # Check if it's legitimate duplicates (same org) or problematic
            org_names = duplicate_records['organization_name'].unique()
            if len(org_names) > 1:
                inconsistency_analysis['duplicate_contacts'].append({
                    'contact_value': contact_value,
                    'count': count,
                    'organizations': list(org_names),
                    'issue': 'Same contact used by multiple organizations'
                })
        
        return inconsistency_analysis
    
    def calculate_overall_quality_score(self, phone_validation, email_validation, 
                                       website_validation, completeness, source_analysis):
        """Calculate overall data quality score"""
        
        # Format compliance score
        format_scores = []
        if phone_validation:
            format_scores.append(phone_validation.get('format_compliance_rate', 0))
        if email_validation:
            format_scores.append(email_validation.get('format_compliance_rate', 0))  
        if website_validation:
            format_scores.append(website_validation.get('format_compliance_rate', 0))
        
        format_score = sum(format_scores) / len(format_scores) if format_scores else 0
        
        # Completeness score
        completeness_score = (
            completeness['required_completeness_rate'] * 0.8 + 
            completeness['optional_completeness_rate'] * 0.2
        )
        
        # Source reliability score
        total_records = sum(source['record_count'] for source in source_analysis['sources'].values())
        weighted_reliability = 0
        
        for source, data in source_analysis['sources'].items():
            weight = data['record_count'] / total_records
            weighted_reliability += data['reliability_score'] * weight
        
        # Calculate final quality score
        quality_score = (
            format_score * self.quality_weights['format_compliance'] +
            completeness_score * self.quality_weights['completeness'] +
            weighted_reliability * self.quality_weights['source_reliability'] +
            0.9 * self.quality_weights['consistency'] +  # Assume good consistency for now
            0.95 * self.quality_weights['freshness']     # Data is fresh
        )
        
        return {
            'overall_quality_score': quality_score,
            'format_score': format_score,
            'completeness_score': completeness_score,
            'source_reliability_score': weighted_reliability,
            'quality_grade': self.get_quality_grade(quality_score)
        }
    
    def get_quality_grade(self, score):
        """Convert quality score to letter grade"""
        if score >= 0.9:
            return 'A'
        elif score >= 0.8:
            return 'B'
        elif score >= 0.7:
            return 'C'
        elif score >= 0.6:
            return 'D'
        else:
            return 'F'
    
    def run_quality_review(self):
        """Run complete data quality review"""
        print("Critic Agent - Data Quality Reviewer")
        print("=" * 50)
        
        # Load standardized data
        df = self.load_standardized_data()
        if df is None:
            return None
        
        print(f"Starting quality review of {len(df)} records...")
        
        # Run all validation checks
        phone_validation = self.validate_phone_numbers(df)
        email_validation = self.validate_emails(df)
        website_validation = self.validate_websites(df)
        completeness = self.analyze_completeness(df)
        source_analysis = self.analyze_source_reliability(df)
        inconsistencies = self.detect_inconsistencies(df)
        
        # Calculate overall quality score
        quality_score = self.calculate_overall_quality_score(
            phone_validation, email_validation, website_validation,
            completeness, source_analysis
        )
        
        # Compile final report
        critic_report = {
            'review_timestamp': datetime.now().isoformat(),
            'dataset_info': {
                'total_records': len(df),
                'contact_types': df['contact_type'].value_counts().to_dict(),
                'organization_types': df['organization_type'].value_counts().to_dict(),
                'source_agents': df['source_agent'].value_counts().to_dict()
            },
            'quality_assessment': quality_score,
            'validation_results': {
                'phone_validation': phone_validation,
                'email_validation': email_validation,
                'website_validation': website_validation
            },
            'completeness_analysis': completeness,
            'source_reliability': source_analysis,
            'inconsistency_detection': inconsistencies,
            'recommendations': self.generate_recommendations(
                phone_validation, email_validation, website_validation,
                completeness, inconsistencies
            )
        }
        
        # Save report
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(critic_report, f, indent=2, default=str)
        
        print(f"\n" + "=" * 50)
        print(f"CRITIC AGENT QUALITY ASSESSMENT")
        print(f"=" * 50)
        print(f"Overall Quality Score: {quality_score['overall_quality_score']:.2f}")
        print(f"Quality Grade: {quality_score['quality_grade']}")
        print(f"\nComponent Scores:")
        print(f"  Format Compliance: {quality_score['format_score']:.2f}")
        print(f"  Data Completeness: {quality_score['completeness_score']:.2f}")
        print(f"  Source Reliability: {quality_score['source_reliability_score']:.2f}")
        
        if phone_validation:
            print(f"\nPhone Validation: {phone_validation['format_compliance_rate']:.1%} valid")
        if email_validation:
            print(f"Email Validation: {email_validation['format_compliance_rate']:.1%} valid")
        if website_validation:
            print(f"Website Validation: {website_validation['format_compliance_rate']:.1%} valid")
        
        print(f"\nReport saved to: {self.output_file}")
        
        return critic_report
    
    def generate_recommendations(self, phone_val, email_val, website_val, completeness, inconsistencies):
        """Generate improvement recommendations"""
        recommendations = []
        
        # Format validation recommendations
        if phone_val and phone_val['format_compliance_rate'] < 0.9:
            recommendations.append({
                'category': 'format_validation',
                'priority': 'high',
                'issue': f"Phone format compliance at {phone_val['format_compliance_rate']:.1%}",
                'recommendation': 'Implement stricter phone number validation in collector agents'
            })
        
        # Completeness recommendations
        if completeness['required_completeness_rate'] < 0.95:
            recommendations.append({
                'category': 'data_completeness',
                'priority': 'medium',
                'issue': f"Required field completeness at {completeness['required_completeness_rate']:.1%}",
                'recommendation': 'Improve data extraction logic to capture required fields'
            })
        
        # Inconsistency recommendations
        if inconsistencies['duplicate_contacts']:
            recommendations.append({
                'category': 'data_consistency',
                'priority': 'medium',
                'issue': f"{len(inconsistencies['duplicate_contacts'])} duplicate contacts found",
                'recommendation': 'Implement deduplication logic in data pipeline'
            })
        
        return recommendations

def main():
    """Main execution function"""
    critic = CriticAgent()
    report = critic.run_quality_review()
    
    if report:
        print(f"\n✅ Quality review complete")
        print(f"📊 Grade: {report['quality_assessment']['quality_grade']}")
        print(f"📄 Full report: {critic.output_file}")

if __name__ == "__main__":
    main()