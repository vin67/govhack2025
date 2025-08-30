import Foundation
import Combine

// MARK: - Family Circle Data Models
struct FamilyMember: Codable, Identifiable, Equatable {
    let id: String
    let name: String
    let phoneNumber: String
    let safeWordQuestion: String
    
    // Computed property to normalize phone number for comparison
    var normalizedPhoneNumber: String {
        phoneNumber.components(separatedBy: CharacterSet.decimalDigits.inverted).joined()
    }
}

// MARK: - Family Circle Manager
class FamilyCircleManager: ObservableObject {
    @Published var familyMembers: [FamilyMember] = []
    
    private let userDefaults = UserDefaults.standard
    private let familyMembersKey = "SavedFamilyMembers"
    
    init() {
        loadFamilyMembers()
    }
    
    // MARK: - Data Loading
    func loadFamilyMembers() {
        // In debug mode, load mock data
        #if DEBUG
        if familyMembers.isEmpty {
            loadMockFamilyMembers()
        }
        #else
        // In release mode, load from UserDefaults
        loadSavedFamilyMembers()
        #endif
    }
    
    private func loadMockFamilyMembers() {
        // First try to load from bundle
        if let url = Bundle.main.url(forResource: "mock_family_circle", withExtension: "json"),
           let data = try? Data(contentsOf: url),
           let mockMembers = try? JSONDecoder().decode([FamilyMember].self, from: data) {
            self.familyMembers = mockMembers
            print("FamilyCircle: Loaded \(mockMembers.count) mock family members from bundle")
            return
        }
        
        // If bundle fails, create hardcoded mock data
        print("FamilyCircle: Bundle load failed, using hardcoded mock data")
        self.familyMembers = [
            FamilyMember(id: "1", name: "Vin", phoneNumber: "+61412345678", safeWordQuestion: "What was the name of our first pet?"),
            FamilyMember(id: "2", name: "Robyn", phoneNumber: "+61423456789", safeWordQuestion: "What street did we live on when we first met?"),
            FamilyMember(id: "3", name: "Adam", phoneNumber: "+61434567890", safeWordQuestion: "What was your favorite childhood movie?"),
            FamilyMember(id: "4", name: "Jordan", phoneNumber: "+61445678901", safeWordQuestion: "What was the name of your first school?")
        ]
        print("FamilyCircle: Created \(self.familyMembers.count) hardcoded family members")
    }
    
    private func loadSavedFamilyMembers() {
        guard let data = userDefaults.data(forKey: familyMembersKey),
              let savedMembers = try? JSONDecoder().decode([FamilyMember].self, from: data) else {
            return
        }
        
        DispatchQueue.main.async {
            self.familyMembers = savedMembers
        }
    }
    
    // MARK: - Data Management
    func addFamilyMember(_ member: FamilyMember) {
        familyMembers.append(member)
        saveFamilyMembers()
    }
    
    func removeFamilyMember(_ member: FamilyMember) {
        familyMembers.removeAll { $0.id == member.id }
        saveFamilyMembers()
    }
    
    func updateFamilyMember(_ member: FamilyMember) {
        if let index = familyMembers.firstIndex(where: { $0.id == member.id }) {
            familyMembers[index] = member
            saveFamilyMembers()
        }
    }
    
    private func saveFamilyMembers() {
        // Don't save mock data in debug mode
        #if DEBUG
        return
        #else
        guard let data = try? JSONEncoder().encode(familyMembers) else { return }
        userDefaults.set(data, forKey: familyMembersKey)
        
        // Also save to App Group for extensions
        saveToAppGroup()
        #endif
    }
    
    private func saveToAppGroup() {
        guard let sharedContainer = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: "group.org.govhack.digitalguardian"),
              let data = try? JSONEncoder().encode(familyMembers) else {
            return
        }
        
        let fileURL = sharedContainer.appendingPathComponent("family_circle.json")
        try? data.write(to: fileURL)
    }
    
    // MARK: - Lookup Functions
    func findFamilyMember(by phoneNumber: String) -> FamilyMember? {
        let normalizedInput = phoneNumber.components(separatedBy: CharacterSet.decimalDigits.inverted).joined()
        
        print("FamilyCircle: Looking for phone: \(phoneNumber) (normalized: \(normalizedInput))")
        print("FamilyCircle: Family members in memory:")
        for member in familyMembers {
            print("  - \(member.name): \(member.phoneNumber) (normalized: \(member.normalizedPhoneNumber))")
        }
        
        return familyMembers.first { member in
            let memberNormalized = member.normalizedPhoneNumber
            // Check for exact match or if one contains the other (for different formats)
            let matches = memberNormalized == normalizedInput || 
                   memberNormalized.hasSuffix(normalizedInput) || 
                   normalizedInput.hasSuffix(memberNormalized)
            if matches {
                print("FamilyCircle: MATCH FOUND - \(member.name)")
            }
            return matches
        }
    }
    
    func isFamilyMember(_ phoneNumber: String) -> Bool {
        return findFamilyMember(by: phoneNumber) != nil
    }
}
