import Foundation

enum RiskLevel {
    case safe
    case threat
    case suspicious
    case unknown
}

struct SMSAnalysisResult {
    let riskLevel: RiskLevel
    let details: String
    let extractedPhoneNumbers: [String]
    let extractedURLs: [String]
    let matchedThreatIndicators: [String]
}

class SMSAnalyzer {
    
    private var verifiedContacts: [VerifiedContact] = []
    private var threatContacts: [ThreatContact] = []
    
    // Scam patterns from our research
    private let scamKeywords = [
        "tax refund", "claim your", "urgent action", "suspend", "verify account",
        "click here", "limited time", "congratulations", "you've won", "act now",
        "confirm details", "update payment", "unusual activity", "security alert"
    ]
    
    private let legitimateDomains = [
        "gov.au", "ato.gov.au", "servicesaustralia.gov.au", "health.gov.au",
        "commbank.com.au", "westpac.com.au", "nab.com.au", "anz.com.au"
    ]
    
    init() {
        loadContactsDatabase()
    }
    
    func analyze(message: String) -> SMSAnalysisResult {
        let lowercasedMessage = message.lowercased()
        
        // Extract phone numbers and URLs
        let phoneNumbers = extractPhoneNumbers(from: message)
        let urls = extractURLs(from: message)
        
        // Check for threats
        var threatIndicators: [String] = []
        var riskLevel: RiskLevel = .unknown
        var details = ""
        
        // 1. Check phone numbers against threat database
        for phone in phoneNumbers {
            if let threat = checkPhoneAgainstThreats(phone) {
                riskLevel = .threat
                threatIndicators.append("Known scam number: \(phone)")
                details = "⛔ \(threat.organizationName)\n❌ \(threat.notes ?? "")"
                break
            }
            
            if let verified = checkPhoneAgainstVerified(phone) {
                riskLevel = .safe
                details = "✓ Verified: \(verified.organizationName)\n✓ \(verified.organizationType)"
            }
        }
        
        // 2. Check URLs for phishing
        for url in urls {
            if isPhishingURL(url) {
                riskLevel = .threat
                threatIndicators.append("Suspicious URL: \(url)")
                details += "\n❌ Suspicious link detected"
            } else if isLegitimateURL(url) {
                if riskLevel != .threat {
                    riskLevel = .safe
                    details += "\n✓ Legitimate website"
                }
            }
        }
        
        // 3. Check for scam keywords
        let detectedKeywords = scamKeywords.filter { lowercasedMessage.contains($0) }
        if !detectedKeywords.isEmpty {
            if riskLevel == .unknown {
                riskLevel = .suspicious
            }
            threatIndicators.append(contentsOf: detectedKeywords.map { "Scam keyword: '\($0)'" })
            details += "\n⚠️ Contains suspicious phrases"
        }
        
        // 4. Check for impersonation
        if message.contains("ATO") || message.contains("Australian Tax") {
            // Check if any phone numbers are actually ATO numbers
            let hasVerifiedATONumber = phoneNumbers.contains { phone in
                if let verified = checkPhoneAgainstVerified(phone) {
                    return verified.organizationName.contains("Tax")
                }
                return false
            }
            
            if !hasVerifiedATONumber && !phoneNumbers.isEmpty {
                riskLevel = .threat
                threatIndicators.append("ATO impersonation - unverified number")
                details = "🚨 Claims to be ATO but number not verified!\n❌ ATO never sends links via SMS"
            }
        }
        
        // 5. Final assessment
        if riskLevel == .unknown && threatIndicators.isEmpty {
            details = "No specific threats detected.\nAlways verify sender independently."
        }
        
        return SMSAnalysisResult(
            riskLevel: riskLevel,
            details: details,
            extractedPhoneNumbers: phoneNumbers,
            extractedURLs: urls,
            matchedThreatIndicators: threatIndicators
        )
    }
    
    func reportScam(message: String) {
        // Save to local storage for community protection
        // In production, this could sync to a server
        if let appGroupURL = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: "group.org.govhack.digitalguardian") {
            let reportedScamsURL = appGroupURL.appendingPathComponent("reported_scams.json")
            
            var reports: [[String: String]] = []
            if let data = try? Data(contentsOf: reportedScamsURL),
               let existing = try? JSONDecoder().decode([[String: String]].self, from: data) {
                reports = existing
            }
            
            reports.append([
                "message": message,
                "date": ISO8601DateFormatter().string(from: Date()),
                "reported_by": "user"
            ])
            
            if let encoded = try? JSONEncoder().encode(reports) {
                try? encoded.write(to: reportedScamsURL)
            }
        }
    }
    
    // MARK: - Database Loading
    
    private func loadContactsDatabase() {
        // Try App Group first (shared with main app)
        if let appGroupURL = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: "group.org.govhack.digitalguardian") {
            let csvURL = appGroupURL.appendingPathComponent("sorted_contacts_master.csv")
            if let data = try? Data(contentsOf: csvURL),
               let csvString = String(data: data, encoding: .utf8) {
                parseCSV(csvString)
                return
            }
        }
        
        // Fallback to bundle
        if let url = Bundle.main.url(forResource: "sorted_contacts_master", withExtension: "csv"),
           let csvString = try? String(contentsOf: url) {
            parseCSV(csvString)
        }
    }
    
    private func parseCSV(_ csvString: String) {
        let lines = csvString.components(separatedBy: .newlines)
        
        for (index, line) in lines.enumerated() {
            if index == 0 { continue } // Skip header
            
            let columns = line.components(separatedBy: ",")
            if columns.count >= 16 {
                let contactType = columns[1]
                let contactValue = columns[2]
                let organizationName = columns[3]
                let riskLevel = columns[15]
                let notes = columns[14]
                
                if riskLevel.lowercased() == "threat" {
                    threatContacts.append(ThreatContact(
                        contactType: contactType,
                        contactValue: contactValue,
                        organizationName: organizationName,
                        notes: notes
                    ))
                } else if riskLevel.lowercased() == "safe" {
                    verifiedContacts.append(VerifiedContact(
                        contactType: contactType,
                        contactValue: contactValue,
                        organizationName: organizationName,
                        organizationType: columns[4]
                    ))
                }
            }
        }
        
        print("SMSAnalyzer: Loaded \(verifiedContacts.count) verified contacts and \(threatContacts.count) threat contacts")
    }
    
    // MARK: - Extraction Methods
    
    private func extractPhoneNumbers(from text: String) -> [String] {
        var phoneNumbers: [String] = []
        
        // Australian phone number patterns
        let patterns = [
            "\\b\\d{4}\\s?\\d{3}\\s?\\d{3}\\b",     // 0400 123 456
            "\\b\\d{2}\\s?\\d{4}\\s?\\d{4}\\b",     // 02 1234 5678
            "\\b1800\\s?\\d{3}\\s?\\d{3}\\b",       // 1800 123 456
            "\\b13\\s?\\d{2}\\s?\\d{2}\\b",         // 13 12 34
            "\\+61\\s?\\d{1}\\s?\\d{4}\\s?\\d{4}"  // +61 4 1234 5678
        ]
        
        for pattern in patterns {
            if let regex = try? NSRegularExpression(pattern: pattern, options: []) {
                let matches = regex.matches(in: text, options: [], range: NSRange(location: 0, length: text.count))
                for match in matches {
                    if let range = Range(match.range, in: text) {
                        phoneNumbers.append(String(text[range]))
                    }
                }
            }
        }
        
        return phoneNumbers
    }
    
    private func extractURLs(from text: String) -> [String] {
        var urls: [String] = []
        
        let pattern = "(https?://[^\\s]+|www\\.[^\\s]+|bit\\.ly/[^\\s]+|tinyurl\\.com/[^\\s]+)"
        
        if let regex = try? NSRegularExpression(pattern: pattern, options: .caseInsensitive) {
            let matches = regex.matches(in: text, options: [], range: NSRange(location: 0, length: text.count))
            for match in matches {
                if let range = Range(match.range, in: text) {
                    urls.append(String(text[range]))
                }
            }
        }
        
        return urls
    }
    
    // MARK: - Verification Methods
    
    private func checkPhoneAgainstThreats(_ phone: String) -> ThreatContact? {
        let normalizedPhone = phone.replacingOccurrences(of: " ", with: "")
        return threatContacts.first { threat in
            threat.contactType == "phone" &&
            threat.contactValue.replacingOccurrences(of: " ", with: "") == normalizedPhone
        }
    }
    
    private func checkPhoneAgainstVerified(_ phone: String) -> VerifiedContact? {
        let normalizedPhone = phone.replacingOccurrences(of: " ", with: "")
        return verifiedContacts.first { verified in
            verified.contactType == "phone" &&
            verified.contactValue.replacingOccurrences(of: " ", with: "") == normalizedPhone
        }
    }
    
    private func isPhishingURL(_ url: String) -> Bool {
        let suspiciousPatterns = [
            "bit.ly", "tinyurl", "shorturl", "ow.ly",  // URL shorteners
            "commonwea1th", "commonwelth",              // Typosquatting
            "at0.gov", "ato-gov", "ato.net"           // Government impersonation
        ]
        
        let lowercasedURL = url.lowercased()
        return suspiciousPatterns.contains { lowercasedURL.contains($0) }
    }
    
    private func isLegitimateURL(_ url: String) -> Bool {
        let lowercasedURL = url.lowercased()
        return legitimateDomains.contains { lowercasedURL.contains($0) }
    }
}

// MARK: - Data Models

struct VerifiedContact {
    let contactType: String
    let contactValue: String
    let organizationName: String
    let organizationType: String
}

struct ThreatContact {
    let contactType: String
    let contactValue: String
    let organizationName: String
    let notes: String?
}