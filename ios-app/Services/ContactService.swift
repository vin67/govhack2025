//
//  ContactService.swift
//  GovHackAntiScam
//
//  Created by GovHack 2025 Team
//

import Foundation
import Combine

class ContactService: ObservableObject {
    @Published var contacts: [Contact] = []
    @Published var threats: [Contact] = []
    @Published var isLoading = false
    @Published var lastUpdated: Date?
    
    // Statistics
    var totalContacts: Int { contacts.count }
    var totalThreats: Int { threats.count }
    var verifiedContacts: Int { contacts.filter { $0.isVerified }.count }
    var safetyRate: Double { 
        totalContacts > 0 ? Double(verifiedContacts) / Double(totalContacts) * 100 : 0 
    }
    
    init() {
        loadContacts()
    }
    
    // MARK: - Data Loading
    
    func loadContacts() {
        isLoading = true
        
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            var allContacts: [Contact] = []
            
            // Load from our CSV files
            allContacts += self?.loadGovernmentContacts() ?? []
            allContacts += self?.loadHospitalContacts() ?? []
            allContacts += self?.loadCharityContacts() ?? []
            
            let threatContacts = self?.loadThreats() ?? []
            
            DispatchQueue.main.async {
                self?.contacts = allContacts.filter { $0.riskLevel == .safe }
                self?.threats = threatContacts
                self?.isLoading = false
                self?.lastUpdated = Date()
            }
        }
    }
    
    private func loadGovernmentContacts() -> [Contact] {
        return loadContactsFromCSV(filename: "government_contacts")
    }
    
    private func loadHospitalContacts() -> [Contact] {
        return loadContactsFromCSV(filename: "hospital_contacts")
    }
    
    private func loadCharityContacts() -> [Contact] {
        return loadContactsFromCSV(filename: "charity_contacts")
    }
    
    private func loadThreats() -> [Contact] {
        return loadContactsFromCSV(filename: "threat_contacts")
    }
    
    private func loadContactsFromCSV(filename: String) -> [Contact] {
        guard let path = Bundle.main.path(forResource: filename, ofType: "csv"),
              let content = try? String(contentsOfFile: path) else {
            print("Could not load \(filename).csv")
            return []
        }
        
        return parseCSV(content: content)
    }
    
    private func parseCSV(content: String) -> [Contact] {
        let lines = content.components(separatedBy: .newlines)
        guard lines.count > 1 else { return [] }
        
        let headers = lines[0].components(separatedBy: ",")
        var contacts: [Contact] = []
        
        for line in lines.dropFirst() {
            guard !line.isEmpty else { continue }
            
            let values = parseCSVLine(line)
            guard values.count == headers.count else { continue }
            
            var csvData: [String: String] = [:]
            for (index, header) in headers.enumerated() {
                csvData[header.trimmingCharacters(in: .whitespacesAndNewlines)] = 
                    values[index].trimmingCharacters(in: .whitespacesAndNewlines)
            }
            
            let contact = Contact(from: csvData)
            contacts.append(contact)
        }
        
        return contacts
    }
    
    private func parseCSVLine(_ line: String) -> [String] {
        var result: [String] = []
        var current = ""
        var inQuotes = false
        
        for char in line {
            if char == "\"" {
                inQuotes.toggle()
            } else if char == "," && !inQuotes {
                result.append(current)
                current = ""
            } else {
                current.append(char)
            }
        }
        
        result.append(current)
        return result
    }
    
    // MARK: - Search and Verification
    
    func searchContact(by phoneNumber: String) -> Contact? {
        let cleanedNumber = cleanPhoneNumber(phoneNumber)
        return contacts.first { cleanPhoneNumber($0.value) == cleanedNumber && $0.type == .phone }
    }
    
    func checkThreat(phoneNumber: String) -> Contact? {
        let cleanedNumber = cleanPhoneNumber(phoneNumber)
        return threats.first { cleanPhoneNumber($0.value) == cleanedNumber }
    }
    
    func verifyContact(phoneNumber: String) -> ScamResult {
        let cleanedNumber = cleanPhoneNumber(phoneNumber)
        
        // Check if it's a known threat first
        if let threat = checkThreat(phoneNumber) {
            return .threat(threat)
        }
        
        // Check if it's a verified safe contact
        if let contact = searchContact(by: phoneNumber) {
            return .verified(contact)
        }
        
        // Unknown number
        return .unknown
    }
    
    func searchContacts(query: String) -> [Contact] {
        guard !query.isEmpty else { return contacts }
        
        return contacts.filter { contact in
            contact.matches(searchText: query)
        }
    }
    
    func getContactsByType(_ type: OrganizationType) -> [Contact] {
        return contacts.filter { $0.organizationType == type }
    }
    
    func getContactsByCategory(_ category: ContactCategory) -> [Contact] {
        return contacts.filter { $0.category == category }
    }
    
    func getContactsByState(_ state: String) -> [Contact] {
        return contacts.filter { $0.state.lowercased() == state.lowercased() }
    }
    
    // MARK: - Utilities
    
    private func cleanPhoneNumber(_ number: String) -> String {
        // Remove all non-numeric characters except +
        let cleaned = number.replacingOccurrences(of: "[^0-9+]", with: "", options: .regularExpression)
        
        // Normalize Australian numbers
        if cleaned.hasPrefix("+61") {
            return "0" + String(cleaned.dropFirst(3))
        } else if cleaned.hasPrefix("61") && cleaned.count > 10 {
            return "0" + String(cleaned.dropFirst(2))
        }
        
        return cleaned
    }
    
    // MARK: - Statistics and Analytics
    
    func getStatsByCategory() -> [ContactCategory: Int] {
        var stats: [ContactCategory: Int] = [:]
        for contact in contacts {
            stats[contact.category, default: 0] += 1
        }
        return stats
    }
    
    func getStatsByState() -> [String: Int] {
        var stats: [String: Int] = [:]
        for contact in contacts {
            stats[contact.state, default: 0] += 1
        }
        return stats
    }
    
    func getRecentVerifications(limit: Int = 10) -> [Contact] {
        return contacts
            .sorted { $0.verifiedDate > $1.verifiedDate }
            .prefix(limit)
            .map { $0 }
    }
}

// MARK: - Mock Data for Testing
extension ContactService {
    static func mock() -> ContactService {
        let service = ContactService()
        service.contacts = Contact.mockData().filter { $0.riskLevel == .safe }
        service.threats = Contact.mockData().filter { $0.riskLevel == .threat }
        return service
    }
}