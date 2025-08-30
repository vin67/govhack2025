//
//  ContactEnums.swift
//  GovHackAntiScam
//
//  Created by GovHack 2025 Team
//

import Foundation
import SwiftUI

enum ContactType: String, CaseIterable, Codable {
    case phone = "phone"
    case email = "email" 
    case website = "website"
    case organization = "organization"
    case general = "general"
    
    var icon: String {
        switch self {
        case .phone: return "phone.fill"
        case .email: return "envelope.fill"
        case .website: return "globe"
        case .organization: return "building.2.fill"
        case .general: return "info.circle.fill"
        }
    }
    
    var displayName: String {
        switch self {
        case .phone: return "Phone"
        case .email: return "Email"
        case .website: return "Website"
        case .organization: return "Organization"
        case .general: return "General"
        }
    }
}

enum OrganizationType: String, CaseIterable, Codable {
    case government = "government"
    case hospital = "hospital"
    case charity = "charity"
    case threat = "threat"
    
    var icon: String {
        switch self {
        case .government: return "building.columns.fill"
        case .hospital: return "cross.fill"
        case .charity: return "heart.fill"
        case .threat: return "exclamationmark.triangle.fill"
        }
    }
    
    var displayName: String {
        switch self {
        case .government: return "Government"
        case .hospital: return "Hospital"
        case .charity: return "Charity"
        case .threat: return "Threat"
        }
    }
    
    var color: Color {
        switch self {
        case .government: return .blue
        case .hospital: return .green
        case .charity: return .purple
        case .threat: return .red
        }
    }
}

enum RiskLevel: String, CaseIterable, Codable {
    case safe = "safe"
    case threat = "threat"
    case unknown = "unknown"
    
    var color: Color {
        switch self {
        case .safe: return .green
        case .threat: return .red
        case .unknown: return .orange
        }
    }
    
    var icon: String {
        switch self {
        case .safe: return "checkmark.shield.fill"
        case .threat: return "xmark.shield.fill"
        case .unknown: return "questionmark.shield.fill"
        }
    }
    
    var displayName: String {
        switch self {
        case .safe: return "Verified Safe"
        case .threat: return "Known Threat"
        case .unknown: return "Unverified"
        }
    }
    
    var description: String {
        switch self {
        case .safe: return "This contact has been verified as legitimate by official sources"
        case .threat: return "⚠️ WARNING: This number is associated with known scams"
        case .unknown: return "This contact hasn't been verified yet"
        }
    }
}

enum ContactCategory: String, CaseIterable, Codable {
    case healthcareServices = "Healthcare Services"
    case governmentServices = "Government Services" 
    case officialServices = "Official Services"
    case communityServices = "Community Services"
    case securityThreats = "Security Threats"
    
    var icon: String {
        switch self {
        case .healthcareServices: return "stethoscope"
        case .governmentServices: return "building.columns"
        case .officialServices: return "checkmark.seal"
        case .communityServices: return "hands.and.sparkles"
        case .securityThreats: return "exclamationmark.triangle"
        }
    }
    
    var color: Color {
        switch self {
        case .healthcareServices: return .green
        case .governmentServices: return .blue
        case .officialServices: return .indigo
        case .communityServices: return .purple
        case .securityThreats: return .red
        }
    }
    
    var shortName: String {
        switch self {
        case .healthcareServices: return "Health"
        case .governmentServices: return "Government"
        case .officialServices: return "Official"
        case .communityServices: return "Community"
        case .securityThreats: return "Threats"
        }
    }
}

// Geographic regions for Australian contacts
enum AustralianState: String, CaseIterable, Codable {
    case nsw = "NSW"
    case vic = "VIC"
    case qld = "QLD"
    case wa = "WA"
    case sa = "SA"
    case tas = "TAS"
    case act = "ACT"
    case nt = "NT"
    case federal = "Federal"
    case unknown = "Unknown"
    
    var fullName: String {
        switch self {
        case .nsw: return "New South Wales"
        case .vic: return "Victoria"
        case .qld: return "Queensland"
        case .wa: return "Western Australia"
        case .sa: return "South Australia"
        case .tas: return "Tasmania"
        case .act: return "Australian Capital Territory"
        case .nt: return "Northern Territory"
        case .federal: return "Federal"
        case .unknown: return "Unknown"
        }
    }
    
    var flag: String {
        switch self {
        case .federal: return "🇦🇺"
        default: return "🏛️"
        }
    }
}

// Scam detection result
enum ScamResult {
    case verified(Contact)
    case threat(Contact)
    case unknown
    
    var isScam: Bool {
        switch self {
        case .threat: return true
        case .verified, .unknown: return false
        }
    }
    
    var alertMessage: String {
        switch self {
        case .verified(let contact):
            return "✅ Verified: \(contact.organizationName)"
        case .threat(let contact):
            return "⚠️ SCAM ALERT: \(contact.organizationName)"
        case .unknown:
            return "❓ Unknown number - be cautious"
        }
    }
    
    var alertColor: Color {
        switch self {
        case .verified: return .green
        case .threat: return .red
        case .unknown: return .orange
        }
    }
}