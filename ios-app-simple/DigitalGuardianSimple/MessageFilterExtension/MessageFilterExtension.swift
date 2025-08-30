import IdentityLookup
import Foundation

class MessageFilterExtension: ILMessageFilterExtension {
    
    override func handle(_ queryRequest: ILMessageFilterQueryRequest, context: ILMessageFilterExtensionContext, completion: @escaping (ILMessageFilterQueryResponse) -> Void) {
        
        // Create the response
        let response = ILMessageFilterQueryResponse()
        
        // Get sender information
        let sender = queryRequest.sender
        let messageBody = queryRequest.messageBody
        
        // Load verified contacts data
        let verificationResult = checkAgainstDatabase(sender: sender, message: messageBody)
        
        switch verificationResult {
        case .verified:
            // Known legitimate sender - allow
            response.action = .allow
        case .scam:
            // Known scam - filter to junk
            response.action = .filter
            response.subAction = .promotion
        case .suspicious:
            // Suspicious patterns - filter with transaction label
            response.action = .filter
            response.subAction = .transaction
        case .unknown:
            // Unknown sender - allow but could add different handling
            response.action = .allow
        }
        
        completion(response)
    }
    
    private func checkAgainstDatabase(sender: String?, message: String?) -> VerificationResult {
        guard let contactsData = loadVerifiedContacts() else {
            return .unknown
        }
        
        // Check against verified government/charity contacts
        if let sender = sender,
           contactsData.verifiedContacts.contains(where: { contact in
               contact.phone?.contains(sender) == true
           }) {
            return .verified
        }
        
        // Check against known scam patterns
        if let message = message?.lowercased() {
            let scamKeywords = [
                "congratulations you've won",
                "click here to claim",
                "urgent action required",
                "verify your account",
                "suspended account",
                "tax refund",
                "government rebate",
                "covid payment",
                "click this link"
            ]
            
            if scamKeywords.contains(where: message.contains) {
                return .scam
            }
        }
        
        // Check for suspicious sender patterns
        if let sender = sender {
            // Random number patterns often used by scammers
            if sender.count > 10 && sender.allSatisfy(\.isNumber) {
                return .suspicious
            }
            
            // Short codes that aren't verified
            if sender.count <= 6 && sender.allSatisfy(\.isNumber) {
                // Check if it's a verified short code
                if !contactsData.verifiedContacts.contains(where: { $0.phone == sender }) {
                    return .suspicious
                }
            }
        }
        
        return .unknown
    }
    
    private func loadVerifiedContacts() -> ContactsDatabase? {
        guard let url = Bundle.main.url(forResource: "sorted_contacts_master", withExtension: "csv"),
              let data = try? Data(contentsOf: url),
              let content = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        var contacts: [VerifiedContact] = []
        let lines = content.components(separatedBy: .newlines)
        
        // Skip header row
        for line in lines.dropFirst() {
            let columns = line.components(separatedBy: ",")
            if columns.count >= 4 {
                let contact = VerifiedContact(
                    name: columns[0].trimmingCharacters(in: .whitespacesAndNewlines),
                    type: columns[1].trimmingCharacters(in: .whitespacesAndNewlines),
                    phone: columns[2].isEmpty ? nil : columns[2].trimmingCharacters(in: .whitespacesAndNewlines),
                    email: columns[3].isEmpty ? nil : columns[3].trimmingCharacters(in: .whitespacesAndNewlines)
                )
                contacts.append(contact)
            }
        }
        
        return ContactsDatabase(verifiedContacts: contacts)
    }
}

// MARK: - Data Models
enum VerificationResult {
    case verified      // Known legitimate contact
    case scam         // Known scam
    case suspicious   // Suspicious patterns
    case unknown      // No information available
}

struct ContactsDatabase {
    let verifiedContacts: [VerifiedContact]
}

struct VerifiedContact {
    let name: String
    let type: String
    let phone: String?
    let email: String?
}