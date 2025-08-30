//
//  DataManager.swift
//  DigitalGuardianSimple
//
//  Manages CSV data loading and contact verification
//

import Foundation
import SwiftUI
import Combine  // Add Combine for ObservableObject

// Contact model matching CSV structure
struct Contact {
    let contactId: String
    let contactType: String
    let contactValue: String
    let organizationName: String
    let organizationType: String
    let sourceAgent: String
    let sourceUrl: String
    let address: String
    let suburb: String
    let state: String
    let postcode: String
    let services: String
    let verifiedDate: String
    let confidenceScore: Double
    let notes: String
    let riskLevel: String
    let priorityScore: Double
    let geographicRegion: String
    let category: String
}

// Verification result
struct VerificationResult {
    let isVerified: Bool
    let riskLevel: String
    let organizationName: String
    let organizationType: String
    let services: String
    let confidenceScore: Double
    let message: String
    
    var isSafe: Bool {
        return riskLevel.lowercased() == "safe"
    }
    
    var isThreat: Bool {
        return riskLevel.lowercased() == "threat" || riskLevel.lowercased() == "suspicious"
    }
}

// Make sure class is final to avoid inheritance issues
final class DataManager: ObservableObject {
    static let shared = DataManager()
    
    @Published var contacts: [Contact] = []
    @Published var isLoading: Bool = false
    @Published var loadError: String? = nil
    
    private init() {
        loadCSVData()
        copyCSVToAppGroup()
    }
    
    // MARK: - App Group Sharing for Extensions
    private func copyCSVToAppGroup() {
        guard let appGroupURL = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: "group.org.govhack.digitalguardian"),
              let bundleURL = Bundle.main.url(forResource: "sorted_contacts_master", withExtension: "csv") else {
            print("DataManager: Could not access App Group or find CSV")
            return
        }
        
        let destinationURL = appGroupURL.appendingPathComponent("sorted_contacts_master.csv")
        
        // Copy if doesn't exist or update if needed
        if !FileManager.default.fileExists(atPath: destinationURL.path) {
            do {
                try FileManager.default.copyItem(at: bundleURL, to: destinationURL)
                print("DataManager: CSV copied to App Group for extensions")
            } catch {
                print("DataManager: Failed to copy CSV - \(error)")
            }
        }
    }
    
    func loadCSVData() {
        isLoading = true
        loadError = nil
        
        // Load the master CSV file with all contact data
        guard let path = Bundle.main.path(forResource: "sorted_contacts_master", ofType: "csv") else {
            // If CSV not found, use sample data
            loadSampleData()
            return
        }
        
        loadCSVFromPath(path)
    }
    
    private func loadCSVFromPath(_ path: String) {
        do {
            let csvString = try String(contentsOfFile: path, encoding: .utf8)
            let rows = csvString.components(separatedBy: .newlines)
            
            // Skip header row
            guard rows.count > 1 else {
                loadError = "CSV file is empty"
                isLoading = false
                loadSampleData()
                return
            }
            
            var loadedContacts: [Contact] = []
            
            for i in 1..<rows.count {
                let row = rows[i]
                if row.isEmpty { continue }
                
                let columns = parseCSVRow(row)
                if columns.count >= 19 {
                    let contact = Contact(
                        contactId: columns[0],
                        contactType: columns[1],
                        contactValue: columns[2],
                        organizationName: columns[3],
                        organizationType: columns[4],
                        sourceAgent: columns[5],
                        sourceUrl: columns[6],
                        address: columns[7],
                        suburb: columns[8],
                        state: columns[9],
                        postcode: columns[10],
                        services: columns[11],
                        verifiedDate: columns[12],
                        confidenceScore: Double(columns[13]) ?? 0.0,
                        notes: columns[14],
                        riskLevel: columns[15],
                        priorityScore: Double(columns[16]) ?? 0.0,
                        geographicRegion: columns[17],
                        category: columns[18]
                    )
                    loadedContacts.append(contact)
                }
            }
            
            DispatchQueue.main.async { [weak self] in
                self?.contacts = loadedContacts
                self?.isLoading = false
                print("Loaded \(loadedContacts.count) contacts from CSV")
            }
            
        } catch {
            loadError = "Failed to load CSV: \(error.localizedDescription)"
            isLoading = false
            loadSampleData()
        }
    }
    
    // Load sample data as fallback
    private func loadSampleData() {
        contacts = [
            Contact(
                contactId: "sample_1",
                contactType: "phone",
                contactValue: "1800 228 333",
                organizationName: "Administrative Appeals Tribunal",
                organizationType: "government",
                sourceAgent: "sample",
                sourceUrl: "",
                address: "",
                suburb: "",
                state: "Federal",
                postcode: "",
                services: "General enquiries",
                verifiedDate: "2025-08-30",
                confidenceScore: 0.9,
                notes: "Federal government directory",
                riskLevel: "safe",
                priorityScore: 0.0,
                geographicRegion: "Federal",
                category: "Official Services"
            ),
            Contact(
                contactId: "sample_2",
                contactType: "phone",
                contactValue: "1900 123 456",
                organizationName: "Known Scam Number",
                organizationType: "scam",
                sourceAgent: "sample",
                sourceUrl: "",
                address: "",
                suburb: "",
                state: "",
                postcode: "",
                services: "Premium rate scam",
                verifiedDate: "2025-08-30",
                confidenceScore: 1.0,
                notes: "Premium rate number - SCAM",
                riskLevel: "threat",
                priorityScore: 1.0,
                geographicRegion: "",
                category: "Scam"
            ),
            Contact(
                contactId: "sample_3",
                contactType: "email",
                contactValue: "enquiries@service.nsw.gov.au",
                organizationName: "Service NSW",
                organizationType: "government",
                sourceAgent: "sample",
                sourceUrl: "",
                address: "",
                suburb: "",
                state: "NSW",
                postcode: "",
                services: "Government services",
                verifiedDate: "2025-08-30",
                confidenceScore: 0.95,
                notes: "Official NSW Government email",
                riskLevel: "safe",
                priorityScore: 0.0,
                geographicRegion: "NSW",
                category: "Official Services"
            ),
            Contact(
                contactId: "sample_4",
                contactType: "website",
                contactValue: "https://www.service.nsw.gov.au",
                organizationName: "Service NSW",
                organizationType: "government",
                sourceAgent: "sample",
                sourceUrl: "",
                address: "",
                suburb: "",
                state: "NSW",
                postcode: "",
                services: "Government services",
                verifiedDate: "2025-08-30",
                confidenceScore: 0.95,
                notes: "Official NSW Government website",
                riskLevel: "safe",
                priorityScore: 0.0,
                geographicRegion: "NSW",
                category: "Official Services"
            ),
            Contact(
                contactId: "sample_5",
                contactType: "email",
                contactValue: "scammer@phishing-site.com",
                organizationName: "Known Phishing Email",
                organizationType: "scam",
                sourceAgent: "sample",
                sourceUrl: "",
                address: "",
                suburb: "",
                state: "",
                postcode: "",
                services: "Phishing scam",
                verifiedDate: "2025-08-30",
                confidenceScore: 1.0,
                notes: "Known phishing email - SCAM",
                riskLevel: "threat",
                priorityScore: 1.0,
                geographicRegion: "",
                category: "Scam"
            )
        ]
        isLoading = false
        print("Loaded sample data")
    }
    
    // Parse CSV row handling commas in quoted fields
    private func parseCSVRow(_ row: String) -> [String] {
        var result: [String] = []
        var currentField = ""
        var inQuotes = false
        
        for char in row {
            if char == "\"" {
                inQuotes.toggle()
            } else if char == "," && !inQuotes {
                result.append(currentField)
                currentField = ""
            } else {
                currentField.append(char)
            }
        }
        result.append(currentField)
        
        return result
    }
    
    // Verify phone number
    func verifyPhoneNumber(_ phoneNumber: String) -> VerificationResult {
        // Clean the phone number (remove spaces, dashes, etc.)
        let cleanedNumber = phoneNumber.replacingOccurrences(of: " ", with: "")
            .replacingOccurrences(of: "-", with: "")
            .replacingOccurrences(of: "(", with: "")
            .replacingOccurrences(of: ")", with: "")
            .replacingOccurrences(of: "+61", with: "0")
        
        // Search for exact match
        if let contact = contacts.first(where: {
            $0.contactType == "phone" &&
            $0.contactValue.replacingOccurrences(of: " ", with: "") == cleanedNumber
        }) {
            return VerificationResult(
                isVerified: true,
                riskLevel: contact.riskLevel,
                organizationName: contact.organizationName,
                organizationType: contact.organizationType,
                services: contact.services,
                confidenceScore: contact.confidenceScore,
                message: contact.riskLevel.lowercased() == "safe"
                    ? "✅ VERIFIED: This is the official number for \(contact.organizationName)"
                    : "🚨 WARNING: This number is associated with \(contact.notes)"
            )
        }
        
        // Check for known scam patterns
        if isKnownScamPattern(cleanedNumber) {
            return VerificationResult(
                isVerified: false,
                riskLevel: "suspicious",
                organizationName: "Unknown",
                organizationType: "unknown",
                services: "",
                confidenceScore: 0.0,
                message: "⚠️ SUSPICIOUS: This number matches known scam patterns"
            )
        }
        
        return VerificationResult(
            isVerified: false,
            riskLevel: "unknown",
            organizationName: "Unknown",
            organizationType: "unknown",
            services: "",
            confidenceScore: 0.0,
            message: "❓ UNKNOWN: This number is not in our database. Be cautious."
        )
    }
    
    // Verify email address
    func verifyEmail(_ email: String) -> VerificationResult {
        let lowercasedEmail = email.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
        
        // Search for exact match
        if let contact = contacts.first(where: {
            $0.contactType == "email" &&
            $0.contactValue.lowercased() == lowercasedEmail
        }) {
            return VerificationResult(
                isVerified: true,
                riskLevel: contact.riskLevel,
                organizationName: contact.organizationName,
                organizationType: contact.organizationType,
                services: contact.services,
                confidenceScore: contact.confidenceScore,
                message: contact.riskLevel.lowercased() == "safe"
                    ? "✅ VERIFIED: Official email for \(contact.organizationName)"
                    : "🚨 WARNING: This email is flagged as \(contact.riskLevel)"
            )
        }
        
        // Check domain
        if let domain = extractDomain(from: lowercasedEmail) {
            if isGovernmentDomain(domain) {
                return VerificationResult(
                    isVerified: true,
                    riskLevel: "safe",
                    organizationName: "Government Domain",
                    organizationType: "government",
                    services: "",
                    confidenceScore: 0.8,
                    message: "✅ LIKELY SAFE: This appears to be a government email domain"
                )
            }
            
            if isKnownScamDomain(domain) {
                return VerificationResult(
                    isVerified: false,
                    riskLevel: "threat",
                    organizationName: "Unknown",
                    organizationType: "scam",
                    services: "",
                    confidenceScore: 0.0,
                    message: "🚨 DANGER: This email domain is associated with known scams"
                )
            }
        }
        
        return VerificationResult(
            isVerified: false,
            riskLevel: "unknown",
            organizationName: "Unknown",
            organizationType: "unknown",
            services: "",
            confidenceScore: 0.0,
            message: "❓ UNKNOWN: This email is not in our database. Verify independently."
        )
    }
    
    // Verify website URL
    func verifyWebsite(_ url: String) -> VerificationResult {
        let cleanedUrl = url.lowercased()
            .replacingOccurrences(of: "https://", with: "")
            .replacingOccurrences(of: "http://", with: "")
            .replacingOccurrences(of: "www.", with: "")
            .trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        
        // Search for website matches
        if let contact = contacts.first(where: {
            $0.contactType == "website" &&
            $0.contactValue.lowercased().contains(cleanedUrl)
        }) {
            return VerificationResult(
                isVerified: true,
                riskLevel: contact.riskLevel,
                organizationName: contact.organizationName,
                organizationType: contact.organizationType,
                services: contact.services,
                confidenceScore: contact.confidenceScore,
                message: contact.riskLevel.lowercased() == "safe"
                    ? "✅ VERIFIED: Official website for \(contact.organizationName)"
                    : "🚨 WARNING: This website is flagged as \(contact.riskLevel)"
            )
        }
        
        // Check for government domains
        if isGovernmentDomain(cleanedUrl) {
            return VerificationResult(
                isVerified: true,
                riskLevel: "safe",
                organizationName: "Government Website",
                organizationType: "government",
                services: "",
                confidenceScore: 0.8,
                message: "✅ LIKELY SAFE: This appears to be an official government website"
            )
        }
        
        // Check for known scam patterns
        if isKnownScamDomain(cleanedUrl) {
            return VerificationResult(
                isVerified: false,
                riskLevel: "threat",
                organizationName: "Unknown",
                organizationType: "scam",
                services: "",
                confidenceScore: 0.0,
                message: "🚨 DANGER: This website matches known scam patterns"
            )
        }
        
        return VerificationResult(
            isVerified: false,
            riskLevel: "unknown",
            organizationName: "Unknown",
            organizationType: "unknown",
            services: "",
            confidenceScore: 0.0,
            message: "❓ UNKNOWN: This website is not in our database. Verify before entering any information."
        )
    }
    
    // Helper functions
    private func isKnownScamPattern(_ phoneNumber: String) -> Bool {
        // Check for premium rate numbers
        if phoneNumber.hasPrefix("190") || phoneNumber.hasPrefix("1900") {
            return true
        }
        // Add more scam patterns as needed
        return false
    }
    
    private func extractDomain(from email: String) -> String? {
        let components = email.components(separatedBy: "@")
        return components.count == 2 ? components[1] : nil
    }
    
    private func isGovernmentDomain(_ domain: String) -> Bool {
        return domain.hasSuffix(".gov.au") ||
               domain.hasSuffix(".gov") ||
               domain.hasSuffix(".nsw.gov.au") ||
               domain.hasSuffix(".vic.gov.au") ||
               domain.hasSuffix(".qld.gov.au") ||
               domain.hasSuffix(".sa.gov.au") ||
               domain.hasSuffix(".wa.gov.au") ||
               domain.hasSuffix(".tas.gov.au") ||
               domain.hasSuffix(".nt.gov.au") ||
               domain.hasSuffix(".act.gov.au")
    }
    
    private func isKnownScamDomain(_ domain: String) -> Bool {
        let scamPatterns = [
            "auspost-tracking",
            "australia-post",
            "mygovau",
            "mygov-au",
            "ato-gov",
            "centrelink-au"
        ]
        
        for pattern in scamPatterns {
            if domain.contains(pattern) {
                return true
            }
        }
        
        return false
    }
}
