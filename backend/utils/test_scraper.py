#!/usr/bin/env python3
"""
Test script for the government services scraper
"""

from gov_services_scraper import GovServicesAgent

def test_single_page():
    """Test scraping a single page"""
    agent = GovServicesAgent()
    
    # Test with just the 'A' page
    test_url = "https://www.directory.gov.au/enquiry-lines/a"
    print(f"Testing with: {test_url}")
    
    services = agent.extract_services_from_page(test_url)
    
    if services:
        print(f"Successfully extracted {len(services)} services")
        print("\nFirst 5 services:")
        for i, service in enumerate(services[:5]):
            print(f"{i+1}. {service['service_name']}")
            print(f"   Phone: {service['phone_number']}")
            print(f"   Hours: {service['hours_of_operation']}")
            print()
            
        # Save test results
        agent.save_to_csv(services, 'test_services.csv')
    else:
        print("No services found")

if __name__ == "__main__":
    test_single_page()