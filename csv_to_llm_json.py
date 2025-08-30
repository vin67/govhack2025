#!/usr/bin/env python3
"""
CSV to LLM-optimized JSON converter for Digital Guardian iOS app
Converts the sorted_contacts_master.csv to a JSON format optimized for LLM RAG queries
"""

import csv
import json
import re
from typing import List, Dict, Any

def extract_keywords(text: str) -> List[str]:
    """Extract relevant keywords from service descriptions for better LLM matching"""
    if not text or text == 'nan':
        return []
    
    # Common government service keywords
    common_words = {
        'the', 'and', 'or', 'in', 'to', 'for', 'of', 'a', 'an', 'is', 'are', 'was', 'were',
        'hours', 'operation', 'business', 'monday', 'friday', 'government', 'federal',
        'information', 'enquiries', 'general', 'service', 'services'
    }
    
    # Extract meaningful keywords
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    keywords = [word for word in words if word not in common_words]
    
    # Remove duplicates and limit to top 8 most relevant
    return list(dict.fromkeys(keywords))[:8]

def clean_organization_name(name: str) -> str:
    """Clean and standardize organization names"""
    if not name or name == 'nan':
        return "Unknown Agency"
    
    # Handle truncated names
    name = name.strip()
    if len(name) > 30 and not name.endswith('.'):
        name += "..."
    
    return name

def standardize_phone(phone: str) -> str:
    """Standardize phone number format"""
    if not phone:
        return ""
    
    # Remove all non-numeric characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Format common Australian patterns
    if cleaned.startswith('1800') or cleaned.startswith('1300') or cleaned.startswith('13'):
        # Toll-free numbers - add spaces for readability
        if len(cleaned) == 10:  # 1800123456
            return f"{cleaned[:4]} {cleaned[4:7]} {cleaned[7:]}"
        elif len(cleaned) == 6:  # 132861
            return f"{cleaned[:3]} {cleaned[3:]}"
    elif cleaned.startswith('+61'):
        # International format
        return cleaned
    
    return cleaned

def csv_to_llm_json(csv_file_path: str, output_file_path: str) -> None:
    """Convert CSV to LLM-optimized JSON"""
    
    services = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Only process phone contacts that are SAFE (no scam numbers)
            if row['contact_type'] != 'phone' or row.get('risk_level', '').lower() != 'safe':
                continue
                
            # Extract and clean key fields
            phone = standardize_phone(row['contact_value'])
            organization = clean_organization_name(row['organization_name'])
            service_desc = row.get('services', '') or ''
            category = row.get('category', 'Official Services')
            region = row.get('geographic_region', 'Federal')
            
            # Generate keywords for better LLM matching
            keywords = extract_keywords(service_desc)
            
            # Add organization name parts as keywords  
            org_keywords = extract_keywords(organization)
            
            # Add common search terms (ATO, hospital, etc.)
            search_terms = []
            if 'tax' in organization.lower() or 'ato' in organization.lower():
                search_terms.extend(['ato', 'tax', 'taxation'])
            if 'hospital' in organization.lower() or 'health' in organization.lower():
                search_terms.extend(['hospital', 'health', 'medical'])
            if 'medicare' in organization.lower() or service_desc.lower():
                search_terms.extend(['medicare', 'health'])
            if 'centrelink' in organization.lower() or service_desc.lower():
                search_terms.extend(['centrelink', 'welfare', 'benefits'])
                
            all_keywords = list(dict.fromkeys(keywords + org_keywords + search_terms))
            
            # Create LLM-optimized entry for common queries like "call ATO" or "hospital phone number"
            service_entry = {
                "id": row.get('contact_id', ''),
                "serviceName": service_desc[:100] + "..." if len(service_desc) > 100 else service_desc,
                "agency": organization,
                "phoneNumber": phone,
                "category": category,
                "region": region,
                "keywords": all_keywords,
                "searchableText": f"{organization} {service_desc} {' '.join(all_keywords)}".lower(),
                "riskLevel": "safe",  # Only safe numbers included
                "confidenceScore": float(row.get('confidence_score', 0.9)),
                "verifiedDate": row.get('verified_date', '').split('T')[0]  # Just the date part
            }
            
            services.append(service_entry)
    
    # Sort by confidence score and organization name for better LLM performance
    services.sort(key=lambda x: (-x['confidenceScore'], x['agency']))
    
    # Create the final JSON structure
    output_data = {
        "version": "1.0",
        "generatedDate": "2025-08-30",
        "totalServices": len(services),
        "description": "Verified SAFE Australian Government Contact Information for Digital Guardian LLM",
        "usage": "This contains ONLY legitimate, verified government contacts. Answer queries like 'call ATO', 'hospital phone number', or 'what service provides X'. Do not make up information not in this data.",
        "services": services
    }
    
    # Write to JSON file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Successfully converted {len(services)} services to LLM JSON format")
    print(f"📄 Output saved to: {output_file_path}")
    print(f"📊 File size: {len(json.dumps(output_data)) / 1024:.1f} KB")

def main():
    """Main conversion process"""
    csv_path = "data/sorted_contacts_master.csv"
    json_path = "ios-app-simple/DigitalGuardianSimple/DigitalGuardianSimple/verified_services.json"
    
    print("🔄 Converting CSV to LLM-optimized JSON...")
    print(f"📂 Input: {csv_path}")
    print(f"📂 Output: {json_path}")
    
    try:
        csv_to_llm_json(csv_path, json_path)
        print("\n🎉 Conversion completed successfully!")
        print("✅ Ready for Core ML LLM integration")
        
        # Show a sample entry
        with open(json_path, 'r') as f:
            data = json.load(f)
            if data['services']:
                print(f"\n📝 Sample entry:")
                print(json.dumps(data['services'][0], indent=2))
                
    except Exception as e:
        print(f"❌ Error during conversion: {e}")

if __name__ == "__main__":
    main()