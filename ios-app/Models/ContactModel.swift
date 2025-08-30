//
//  ContactModel.swift
//  GovHackAntiScam
//
//  Created by GovHack 2025 Team
//

import Foundation
import SwiftUI

struct Contact: Identifiable, Codable, Hashable {
    let id: String                    // contact_id from CSV
    let type: ContactType            // phone, email, website, organization
    let value: String                // phone number, email, URL
    let organizationName: String     // organization_name from CSV  
    let organizationType: OrganizationType  // government, hospital, charity, threat
    let riskLevel: RiskLevel         // safe, threat
    let state: String                // NSW, Federal, etc.
    let category: ContactCategory    // Healthcare, Government Services, etc.
    let confidenceScore: Double      // 0.0 - 1.0
    let verifiedDate: Date
    let notes: String
    let sourceAgent: String          // Which agent collected this data
    
    // Computed properties for UI
    var isVerified: Bool { 
        riskLevel == .safe && confidenceScore >= 0.7 
    }
    
    var displayName: String {
        organizationName.isEmpty ? value : organizationName
    }
    
    var formattedPhoneNumber: String {
        guard type == .phone else { return value }
        return formatAustralianPhoneNumber(value)
    }
    
    var verificationBadge: String {
        switch riskLevel {
        case .safe: return "✅"
        case .threat: return "⚠️"  
        case .unknown: return "❓"
        }
    }
    
    // Initialize from CSV row data
    init(from csvData: [String: String]) {
        self.id = csvData["contact_id"] ?? UUID().uuidString
        self.type = ContactType(rawValue: csvData["contact_type"] ?? "phone") ?? .phone
        self.value = csvData["contact_value"] ?? ""
        self.organizationName = csvData["organization_name"] ?? ""
        self.organizationType = OrganizationType(rawValue: csvData["organization_type"] ?? "government") ?? .government
        self.riskLevel = RiskLevel(rawValue: csvData["risk_level"] ?? "unknown") ?? .unknown
        self.state = csvData["state"] ?? csvData["geographic_region"] ?? "Unknown"
        self.category = ContactCategory(rawValue: csvData["category"] ?? "Government Services") ?? .governmentServices
        self.confidenceScore = Double(csvData["confidence_score"] ?? "0.7") ?? 0.7
        self.notes = csvData["notes"] ?? ""
        self.sourceAgent = csvData["source_agent"] ?? "unknown"
        
        // Parse verified_date
        let dateFormatter = ISO8601DateFormatter()
        self.verifiedDate = dateFormatter.date(from: csvData["verified_date"] ?? "") ?? Date()
    }
    
    // Helper function for phone number formatting
    private func formatAustralianPhoneNumber(_ number: String) -> String {
        let cleaned = number.replacingOccurrences(of: "[^0-9]", with: "", options: .regularExpression)
        
        // Handle different Australian phone formats
        if cleaned.hasPrefix("61") && cleaned.count > 10 {
            // International format: +61 X XXXX XXXX
            let withoutCountryCode = String(cleaned.dropFirst(2))
            return "+61 " + formatDomesticNumber(withoutCountryCode)
        } else if cleaned.hasPrefix("0") && cleaned.count == 10 {
            // Domestic format: 0X XXXX XXXX
            return formatDomesticNumber(cleaned)
        } else if cleaned.hasPrefix("1800") || cleaned.hasPrefix("1300") {
            // Toll-free: 1800 XXX XXX
            return formatTollFree(cleaned)
        }
        
        return number // Return original if no formatting applied
    }
    
    private func formatDomesticNumber(_ number: String) -> String {
        if number.count == 10 {
            let area = String(number.prefix(2))
            let first = String(number.dropFirst(2).prefix(4))
            let second = String(number.dropFirst(6))
            return "\(area) \(first) \(second)"
        }
        return number
    }
    
    private func formatTollFree(_ number: String) -> String {
        if number.count == 10 {
            let prefix = String(number.prefix(4))
            let first = String(number.dropFirst(4).prefix(3))
            let second = String(number.dropFirst(7))
            return "\(prefix) \(first) \(second)"
        }
        return number
    }
}

// Extension for easy searching and filtering
extension Contact {
    func matches(searchText: String) -> Bool {
        let lowercaseSearch = searchText.lowercased()
        return organizationName.lowercased().contains(lowercaseSearch) ||
               value.contains(searchText) ||
               category.rawValue.lowercased().contains(lowercaseSearch) ||
               state.lowercased().contains(lowercaseSearch)
    }
    
    static func mockData() -> [Contact] {
        return [
            Contact(from: [
                "contact_id": "gov_001",
                "contact_type": "phone", 
                "contact_value": "1800 020 103",
                "organization_name": "Australian Taxation Office",
                "organization_type": "government",
                "risk_level": "safe",
                "state": "Federal",
                "category": "Government Services",
                "confidence_score": "0.95",
                "verified_date": "2025-08-30T10:47:23Z",
                "notes": "Official ATO contact line",
                "source_agent": "government_services_scraper"
            ]),
            Contact(from: [
                "contact_id": "threat_001",
                "contact_type": "phone",
                "contact_value": "1800 595 160", 
                "organization_name": "SCAM: Fake ACCC calls",
                "organization_type": "threat",
                "risk_level": "threat",
                "state": "Unknown",
                "category": "Security Threats",
                "confidence_score": "0.8",
                "verified_date": "2025-08-30T10:47:23Z",
                "notes": "Known scam number spoofing ACCC",
                "source_agent": "scamwatch_threat_agent"
            ])
        ]
    }
}