//
//  CSVDataLoader.swift
//  GovHackAntiScam
//
//  Created by GovHack 2025 Team
//  Data integration with backend pipeline CSV files
//

import Foundation

class CSVDataLoader {
    static let shared = CSVDataLoader()
    
    private init() {}
    
    // Path to the backend data directory relative to project
    private var dataDirectory: URL? {
        guard let projectRoot = Bundle.main.url(forResource: "govhack2025", withExtension: nil),
              let dataURL = projectRoot.appendingPathComponent("data") else {
            // Fallback: look in bundle for CSV files
            return Bundle.main.bundleURL
        }
        return dataURL
    }
    
    func loadVerifiedContacts() -> [Contact] {
        var allContacts: [Contact] = []
        
        // Load from all verified CSV files
        allContacts += loadCSVFile(filename: "government_contacts", subfolder: "verified")
        allContacts += loadCSVFile(filename: "hospital_contacts", subfolder: "verified") 
        allContacts += loadCSVFile(filename: "charity_contacts", subfolder: "verified")
        
        return allContacts.filter { $0.riskLevel == .safe }
    }
    
    func loadThreatContacts() -> [Contact] {
        return loadCSVFile(filename: "threat_contacts", subfolder: "verified")
            .filter { $0.riskLevel == .threat }
    }
    
    private func loadCSVFile(filename: String, subfolder: String) -> [Contact] {
        // Try to load from project data directory first
        if let dataDir = dataDirectory {
            let csvPath = dataDir
                .appendingPathComponent(subfolder)
                .appendingPathComponent("\(filename).csv")
            
            if let content = try? String(contentsOf: csvPath) {
                return parseCSVContent(content)
            }
        }
        
        // Fallback: load from app bundle
        guard let bundlePath = Bundle.main.path(forResource: filename, ofType: "csv"),
              let content = try? String(contentsOfFile: bundlePath) else {
            print("⚠️ Could not load \(filename).csv from bundle or project directory")
            return []
        }
        
        return parseCSVContent(content)
    }
    
    private func parseCSVContent(_ content: String) -> [Contact] {
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
}

// Extension to update ContactService to use shared data
extension ContactService {
    func loadContactsFromBackend() {
        isLoading = true
        
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            let verifiedContacts = CSVDataLoader.shared.loadVerifiedContacts()
            let threatContacts = CSVDataLoader.shared.loadThreatContacts()
            
            DispatchQueue.main.async {
                self?.contacts = verifiedContacts
                self?.threats = threatContacts
                self?.isLoading = false
                self?.lastUpdated = Date()
                
                print("📊 Loaded \(verifiedContacts.count) verified contacts, \(threatContacts.count) threats from backend")
            }
        }
    }
}