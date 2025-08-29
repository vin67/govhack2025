#!/usr/bin/env python3
"""
Sorter Agent - Data Categorization and Risk Assessment
Categorizes standardized contact data by organization type, risk level, and priority
Part of the multi-agent framework with Google A2A protocol
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import asyncio

class SorterAgent:
    def __init__(self):
        self.agent_id = "sorter_agent"
        self.input_file = 'data/standardized_contacts.csv'
        self.quality_report_file = 'data/reports/critic_report.json'
        
        # Risk assessment criteria
        self.risk_levels = {
            'safe': 'Verified legitimate contact',
            'suspicious': 'Needs manual verification', 
            'threat': 'Known scam indicator',
            'unknown': 'Insufficient data for assessment'
        }
        
        # Priority levels for different contact types
        self.priority_mapping = {
            'government': {'priority': 1, 'category': 'Official Services'},
            'hospital': {'priority': 2, 'category': 'Healthcare Services'},
            'charity': {'priority': 3, 'category': 'Community Services'},
            'threat': {'priority': 4, 'category': 'Security Threats'}
        }
    
    def load_data_and_quality_report(self):
        """Load standardized data and quality assessment"""
        print("Sorter Agent - Data Categorization System")
        print("=" * 50)
        
        # Load standardized contacts
        contacts_path = Path(self.input_file)
        if not contacts_path.exists():
            print(f"Error: {self.input_file} not found")
            return None, None
        
        df = pd.read_csv(contacts_path)
        print(f"Loaded {len(df)} standardized contact records")
        
        # Load quality report
        quality_path = Path(self.quality_report_file)
        quality_report = None
        if quality_path.exists():
            with open(quality_path, 'r') as f:
                quality_report = json.load(f)
            print(f"Loaded quality assessment report (Grade: {quality_report['quality_assessment']['quality_grade']})")
        else:
            print("Warning: No quality report found, proceeding without quality metrics")
        
        return df, quality_report
    
    def assess_risk_level(self, row):
        """Assess risk level for each contact record"""
        org_type = row['organization_type'].lower()
        confidence = row['confidence_score']
        contact_value = str(row['contact_value']).strip()
        
        # Threat indicators are high risk
        if org_type == 'threat':
            return 'threat'
        
        # Government and hospitals are generally safe if high confidence
        if org_type in ['government', 'hospital'] and confidence >= 0.8:
            return 'safe'
        
        # Charities with good confidence are safe
        if org_type == 'charity' and confidence >= 0.7:
            return 'safe'
        
        # Low confidence requires manual verification
        if confidence < 0.6:
            return 'suspicious'
        
        # Check for suspicious patterns in phone numbers
        if row['contact_type'] == 'phone':
            # Very short numbers might be suspicious
            clean_number = ''.join(c for c in contact_value if c.isdigit())
            if len(clean_number) < 8:
                return 'suspicious'
            
            # Repeated digits pattern
            if len(set(clean_number)) <= 2:
                return 'suspicious'
        
        return 'safe'
    
    def calculate_priority_score(self, row, quality_metrics=None):
        """Calculate priority score for contact sorting"""
        org_type = row['organization_type'].lower()
        base_priority = self.priority_mapping.get(org_type, {}).get('priority', 5)
        
        # Adjust based on confidence score
        confidence_bonus = row['confidence_score'] * 10  # 0-10 points
        
        # Boost priority for emergency services
        emergency_keywords = ['emergency', 'police', 'ambulance', 'fire', 'rescue', '000']
        if any(keyword in str(row['organization_name']).lower() for keyword in emergency_keywords):
            base_priority = 0  # Highest priority
        
        # Boost for toll-free numbers (often important services)
        if row['contact_type'] == 'phone' and str(row['contact_value']).strip().startswith(('1800', '1300')):
            confidence_bonus += 2
        
        # Government domains get priority boost
        if row['contact_type'] == 'email' and '.gov.au' in str(row['contact_value']).lower():
            confidence_bonus += 3
        
        # Final score (lower is higher priority)
        final_score = base_priority - (confidence_bonus / 10)
        return max(0, final_score)  # Ensure non-negative
    
    def categorize_by_geography(self, row):
        """Categorize contacts by geographic region"""
        state = str(row.get('state', '')).upper()
        org_name = str(row['organization_name']).lower()
        
        if state == 'FEDERAL' or 'federal' in org_name:
            return 'Federal'
        elif state == 'NSW':
            return 'NSW'
        elif state in ['VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT']:
            return state
        else:
            return 'Unknown'
    
    def sort_and_categorize_data(self, df, quality_report=None):
        """Main sorting and categorization logic"""
        print(f"\nSorting and categorizing {len(df)} contact records...")
        
        # Add computed fields
        df['risk_level'] = df.apply(self.assess_risk_level, axis=1)
        df['priority_score'] = df.apply(lambda row: self.calculate_priority_score(row, quality_report), axis=1)
        df['geographic_region'] = df.apply(self.categorize_by_geography, axis=1)
        df['category'] = df['organization_type'].map(lambda x: self.priority_mapping.get(x, {}).get('category', 'Other'))
        
        # Sort by priority score (ascending - lower scores = higher priority)
        df_sorted = df.sort_values(['priority_score', 'confidence_score'], ascending=[True, False])
        
        # Generate statistics
        stats = {
            'total_records': len(df),
            'by_organization_type': df['organization_type'].value_counts().to_dict(),
            'by_contact_type': df['contact_type'].value_counts().to_dict(),
            'by_risk_level': df['risk_level'].value_counts().to_dict(),
            'by_geographic_region': df['geographic_region'].value_counts().to_dict(),
            'by_category': df['category'].value_counts().to_dict(),
            'average_confidence': df['confidence_score'].mean(),
            'high_priority_count': len(df[df['priority_score'] < 2]),
            'safe_contacts': len(df[df['risk_level'] == 'safe']),
            'threat_indicators': len(df[df['risk_level'] == 'threat'])
        }
        
        print(f"  ✅ Sorting complete")
        print(f"  📊 Risk Assessment:")
        for risk, count in stats['by_risk_level'].items():
            print(f"    {risk.title()}: {count} contacts")
        
        return df_sorted, stats
    
    def generate_categorized_outputs(self, df_sorted, stats):
        """Generate separate CSV files for each category"""
        print(f"\nGenerating categorized output files...")
        
        output_files = {}
        
        # 1. By Organization Type
        for org_type in df_sorted['organization_type'].unique():
            org_data = df_sorted[df_sorted['organization_type'] == org_type]
            filename = f"data/verified/{org_type}_contacts.csv"
            org_data.to_csv(filename, index=False)
            output_files[filename] = len(org_data)
            print(f"  📄 {filename}: {len(org_data)} records")
        
        # 2. By Risk Level
        for risk_level in ['safe', 'threat', 'suspicious']:
            risk_data = df_sorted[df_sorted['risk_level'] == risk_level]
            if len(risk_data) > 0:
                if risk_level == "threat":
                    filename = f"data/threats/{risk_level}_contacts.csv"
                else:
                    filename = f"data/verified/all_{risk_level}_contacts.csv"  # Avoid duplicate with org-type files
                risk_data.to_csv(filename, index=False)
                output_files[filename] = len(risk_data)
                print(f"  🔒 {filename}: {len(risk_data)} records")
        
        # 3. High Priority Contacts (for emergency response)
        high_priority = df_sorted[df_sorted['priority_score'] < 2]
        if len(high_priority) > 0:
            filename = "data/verified/high_priority_contacts.csv"
            high_priority.to_csv(filename, index=False)
            output_files[filename] = len(high_priority)
            print(f"  ⚡ {filename}: {len(high_priority)} records")
        
        # 4. Master sorted file
        filename = "data/sorted_contacts_master.csv"
        df_sorted.to_csv(filename, index=False)
        output_files[filename] = len(df_sorted)
        print(f"  📋 {filename}: {len(df_sorted)} records (complete sorted dataset)")
        
        return output_files
    
    def generate_sorting_report(self, stats, output_files, quality_report=None):
        """Generate comprehensive sorting report"""
        report = {
            'sorting_timestamp': datetime.now().isoformat(),
            'agent_info': {
                'agent_id': self.agent_id,
                'version': '1.0',
                'processing_complete': True
            },
            'input_data': {
                'source_file': self.input_file,
                'total_records_processed': stats['total_records'],
                'quality_grade': quality_report['quality_assessment']['quality_grade'] if quality_report else 'Unknown'
            },
            'categorization_results': {
                'by_organization_type': stats['by_organization_type'],
                'by_contact_type': stats['by_contact_type'],
                'by_risk_level': stats['by_risk_level'],
                'by_geographic_region': stats['by_geographic_region'],
                'by_category': stats['by_category']
            },
            'quality_metrics': {
                'average_confidence_score': round(stats['average_confidence'], 3),
                'high_priority_contacts': stats['high_priority_count'],
                'safe_contacts': stats['safe_contacts'],
                'threat_indicators': stats['threat_indicators'],
                'safety_rate': round((stats['safe_contacts'] / stats['total_records']) * 100, 1)
            },
            'output_files': output_files,
            'anti_scam_summary': {
                'verified_safe_contacts': stats['safe_contacts'],
                'threat_indicators_identified': stats['threat_indicators'],
                'contacts_requiring_verification': stats['by_risk_level'].get('suspicious', 0),
                'ready_for_whitelist': stats['safe_contacts'],
                'ready_for_blacklist': stats['threat_indicators']
            },
            'recommendations': self.generate_recommendations(stats)
        }
        
        # Save report
        report_filename = 'data/reports/sorter_report.json'
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Sorting report saved to: {report_filename}")
        
        return report
    
    def generate_recommendations(self, stats):
        """Generate actionable recommendations based on sorting results"""
        recommendations = []
        
        # Safety recommendations
        safety_rate = (stats['safe_contacts'] / stats['total_records']) * 100
        if safety_rate < 90:
            recommendations.append({
                'category': 'safety',
                'priority': 'high',
                'issue': f"Safety rate at {safety_rate:.1f}%",
                'recommendation': 'Review data collection sources and validation rules'
            })
        
        # Threat detection recommendations
        if stats['threat_indicators'] > 0:
            recommendations.append({
                'category': 'security',
                'priority': 'critical',
                'issue': f"{stats['threat_indicators']} threat indicators found",
                'recommendation': 'Immediately blacklist identified threat contacts'
            })
        
        # Data completeness recommendations
        if stats['by_risk_level'].get('suspicious', 0) > 0:
            recommendations.append({
                'category': 'data_quality',
                'priority': 'medium',
                'issue': f"{stats['by_risk_level']['suspicious']} contacts need verification",
                'recommendation': 'Manual verification required for suspicious contacts'
            })
        
        return recommendations
    
    async def run_sorting_pipeline(self):
        """Run the complete sorting pipeline"""
        # Load data
        df, quality_report = self.load_data_and_quality_report()
        if df is None:
            return None
        
        # Sort and categorize
        df_sorted, stats = self.sort_and_categorize_data(df, quality_report)
        
        # Generate outputs
        output_files = self.generate_categorized_outputs(df_sorted, stats)
        
        # Generate report
        report = self.generate_sorting_report(stats, output_files, quality_report)
        
        # Display summary
        print(f"\n" + "=" * 50)
        print(f"SORTER AGENT COMPLETION SUMMARY")
        print(f"=" * 50)
        print(f"📊 Processed: {stats['total_records']} contact records")
        print(f"🛡️ Safe Contacts: {stats['safe_contacts']} ({(stats['safe_contacts']/stats['total_records']*100):.1f}%)")
        print(f"🚨 Threat Indicators: {stats['threat_indicators']}")
        print(f"📋 Output Files: {len(output_files)}")
        print(f"⚡ High Priority: {stats['high_priority_count']} contacts")
        
        return report

def main():
    """Main execution function"""
    import asyncio
    
    sorter = SorterAgent()
    report = asyncio.run(sorter.run_sorting_pipeline())
    
    if report:
        print(f"\n✅ Sorting pipeline complete")
        print(f"📄 Report: sorter_report.json")
        print(f"🎯 Ready for anti-scam deployment")

if __name__ == "__main__":
    main()