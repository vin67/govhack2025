#!/usr/bin/env python3
"""
Analysis script for the extracted government services data
"""

import csv
import re
from collections import Counter

def analyze_services_data():
    """Analyze the extracted government services data"""
    
    services = []
    phone_types = []
    departments = []
    
    with open('government_services.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            services.append(row)
            
            # Analyze phone number types
            phone = row['phone_number']
            if phone.startswith('1800'):
                phone_types.append('1800 (Toll Free)')
            elif phone.startswith('1300'):
                phone_types.append('1300 (Local Rate)')
            elif phone.startswith('131') or phone.startswith('13 '):
                phone_types.append('13X (National)')
            elif re.match(r'\(0[2-8]\)', phone):
                phone_types.append('State/Territory')
            else:
                phone_types.append('Other')
                
            # Extract department/agency from service name
            service_name = row['service_name']
            if 'ATO' in service_name or 'Taxation' in service_name:
                departments.append('Australian Taxation Office')
            elif 'Passport' in service_name:
                departments.append('Foreign Affairs & Trade')
            elif 'Veterans' in service_name or 'DVA' in service_name:
                departments.append('Veterans Affairs')
            elif 'Health' in service_name or 'Medical' in service_name:
                departments.append('Health')
            elif 'Centrelink' in service_name or 'Social' in service_name:
                departments.append('Social Services')
            else:
                departments.append('Other')
    
    print("Government Services Dataset Analysis")
    print("==================================")
    print(f"Total Services Extracted: {len(services)}")
    print()
    
    print("Phone Number Types:")
    phone_counts = Counter(phone_types)
    for phone_type, count in phone_counts.most_common():
        print(f"  {phone_type}: {count}")
    print()
    
    print("Department Categories:")
    dept_counts = Counter(departments)
    for dept, count in dept_counts.most_common():
        print(f"  {dept}: {count}")
    print()
    
    # Services with 24-hour availability
    emergency_services = []
    for service in services:
        hours = service['hours_of_operation'].lower()
        if '24' in hours or 'emergency' in hours:
            emergency_services.append(service['service_name'])
    
    if emergency_services:
        print("24-Hour/Emergency Services:")
        for service in emergency_services:
            print(f"  - {service}")
        print()
    
    # Show services with comprehensive descriptions
    detailed_services = []
    for service in services:
        if len(service['description']) > 100:
            detailed_services.append(service['service_name'])
    
    print(f"Services with detailed descriptions: {len(detailed_services)}")
    print()
    
    print("Sample High-Value Services:")
    priority_keywords = ['emergency', 'passport', 'tax', 'centrelink', 'medicare', 'veterans']
    for service in services[:20]:  # Check first 20
        service_name_lower = service['service_name'].lower()
        if any(keyword in service_name_lower for keyword in priority_keywords):
            print(f"  - {service['service_name']}: {service['phone_number']}")

if __name__ == "__main__":
    analyze_services_data()