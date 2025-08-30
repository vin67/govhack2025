import Foundation
import UserNotifications
import SwiftUI
import Combine

// MARK: - Notification Handler
class NotificationHandler: NSObject, ObservableObject {
    @Published var lastNotificationData: [String: Any] = [:]
    
    override init() {
        super.init()
        UNUserNotificationCenter.current().delegate = self
    }
    
    // Handle notification tap actions
    func handleNotificationAction(_ actionIdentifier: String, userInfo: [AnyHashable: Any]) {
        guard let familyMemberId = userInfo["familyMemberId"] as? String,
              let familyMemberName = userInfo["familyMemberName"] as? String,
              let safeWordQuestion = userInfo["safeWordQuestion"] as? String else {
            return
        }
        
        switch actionIdentifier {
        case "VIEW_SAFE_WORD":
            // Show safe word question in app
            showSafeWordQuestion(name: familyMemberName, question: safeWordQuestion)
            
        case "SECURE_CALLBACK":
            // Trigger secure callback flow
            initiateSecureCallback(familyMemberId: familyMemberId, name: familyMemberName)
            
        default:
            break
        }
    }
    
    private func showSafeWordQuestion(name: String, question: String) {
        DispatchQueue.main.async {
            self.lastNotificationData = [
                "action": "show_safe_word",
                "name": name,
                "question": question,
                "timestamp": Date()
            ]
        }
        
        // Could also show an alert or navigate to a specific view
        print("NotificationHandler: Safe word question for \(name): \(question)")
    }
    
    private func initiateSecureCallback(familyMemberId: String, name: String) {
        DispatchQueue.main.async {
            self.lastNotificationData = [
                "action": "secure_callback",
                "familyMemberId": familyMemberId,
                "name": name,
                "timestamp": Date()
            ]
        }
        
        // Could trigger phone app or show verification screen
        print("NotificationHandler: Secure callback initiated for \(name)")
    }
}

// MARK: - UNUserNotificationCenterDelegate
extension NotificationHandler: UNUserNotificationCenterDelegate {
    // Handle notification when app is in foreground
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        let userInfo = notification.request.content.userInfo
        
        // If this is already a processed notification, just show it
        if userInfo["type"] != nil {
            completionHandler([.banner, .sound])
            return
        }
        
        // Process the notification through our verification system
        if let phoneNumber = userInfo["phoneNumber"] as? String ?? userInfo["handle"] as? String {
            // Process and replace the notification
            let familyManager = FamilyCircleManager()
            familyManager.loadFamilyMembers()
            
            if let familyMember = familyManager.findFamilyMember(by: phoneNumber) {
                // Modify the notification content directly
                print("NotificationHandler: Showing family notification for \(familyMember.name)")
                // Show a banner with the safe word info
                completionHandler([.banner, .sound])
            } else {
                // Show notification normally
                completionHandler([.banner, .sound])
            }
            
            // Also schedule our custom notification
            processAndShowCustomNotification(phoneNumber: phoneNumber, userInfo: userInfo)
        } else {
            // Show notification even when app is open
            completionHandler([.banner, .sound])
        }
    }
    
    // Handle notification tap
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let userInfo = response.notification.request.content.userInfo
        handleNotificationAction(response.actionIdentifier, userInfo: userInfo)
        
        completionHandler()
    }
    
    private func processAndShowCustomNotification(phoneNumber: String, userInfo: [AnyHashable: Any]) {
        let familyManager = FamilyCircleManager()
        familyManager.loadFamilyMembers() // Make sure family members are loaded
        let dataManager = DataManager.shared
        
        print("NotificationHandler: Processing call from \(phoneNumber)")
        print("NotificationHandler: Family members loaded: \(familyManager.familyMembers.count)")
        
        // Step 1: Check if it's a family member
        if let familyMember = familyManager.findFamilyMember(by: phoneNumber) {
            print("NotificationHandler: Found family member - \(familyMember.name)")
            // Create gentle nudge with safe word  
            scheduleProcessedNotification(
                title: "🛡️ ✅ SAFE - Family: \(familyMember.name)",
                body: "💚 Safe word: \(familyMember.safeWordQuestion)\n✓ This is your trusted contact",
                type: .familyCall,
                phoneNumber: phoneNumber
            )
            return
        } else {
            print("NotificationHandler: Not a family member, checking verified contacts...")
        }
        
        // Step 2: Check against verified contacts database
        let verificationResult = dataManager.verifyPhoneNumber(phoneNumber)
        print("NotificationHandler: Verification result - verified: \(verificationResult.isVerified), risk: \(verificationResult.riskLevel)")
        
        if verificationResult.isVerified && verificationResult.isSafe {
            // Known legitimate number
            scheduleProcessedNotification(
                title: "🛡️ ✅ VERIFIED - Government",
                body: "💚 \(verificationResult.organizationName)\n✓ Official verified contact",
                type: .verified,
                phoneNumber: phoneNumber
            )
            
        } else if verificationResult.isThreat {
            // Known scam number
            scheduleProcessedNotification(
                title: "⚠️ 🚨 DANGER - SCAM DETECTED 🚨",
                body: "❌ DO NOT ANSWER!\n⛔ Known scam number\n🚫 Block immediately\n☎️ Report to ScamWatch",
                type: .scam,
                phoneNumber: phoneNumber
            )
            
        } else {
            // Unknown number - no special processing needed
            print("NotificationHandler: Unknown number, no special notification")
        }
    }
    
    private func scheduleProcessedNotification(title: String, body: String, type: NotificationType, phoneNumber: String) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = type == .scam ? .default : nil
        content.userInfo = ["phoneNumber": phoneNumber, "type": type.rawValue]
        
        // Add category for family calls
        if type == .familyCall {
            content.categoryIdentifier = "FAMILY_CALL_REMINDER"
        }
        
        let request = UNNotificationRequest(
            identifier: "processed_\(phoneNumber)_\(Date().timeIntervalSince1970)",
            content: content,
            trigger: nil // Immediate delivery
        )
        
        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("NotificationHandler: Failed to schedule notification - \(error)")
            } else {
                print("NotificationHandler: Successfully scheduled \(type.rawValue) notification")
            }
        }
    }
}

enum NotificationType: String {
    case familyCall = "family_call"
    case verified = "verified"
    case scam = "scam"
    case unknown = "unknown"
}