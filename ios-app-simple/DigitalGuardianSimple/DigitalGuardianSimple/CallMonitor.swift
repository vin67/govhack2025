import Foundation
import CallKit
import UserNotifications
import SwiftUI
import Combine

// MARK: - Call Monitor
class CallMonitor: NSObject, ObservableObject {
    private let callObserver = CXCallObserver()
    private let familyManager = FamilyCircleManager()
    
    @Published var isMonitoring = false
    @Published var lastCallStatus = "Idle"
    
    override init() {
        super.init()
        setupCallObserver()
        requestNotificationPermission()
    }
    
    // MARK: - Call Observer Setup
    private func setupCallObserver() {
        callObserver.setDelegate(self, queue: DispatchQueue.main)
        isMonitoring = true
        print("CallMonitor: Call observer initialized")
    }
    
    // MARK: - Notification Permissions
    private func requestNotificationPermission() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            DispatchQueue.main.async {
                if granted {
                    print("CallMonitor: Notification permission granted")
                } else {
                    print("CallMonitor: Notification permission denied")
                }
            }
        }
    }
    
    // MARK: - Family Member Detection
    private func handleCallConnected(_ call: CXCall) {
        // For now, we'll use a placeholder approach since CXCall doesn't expose remoteHandle directly
        // In a real implementation, you'd need to track calls through other means
        let phoneNumber = "Unknown" // Placeholder
        
        print("CallMonitor: Call connected - checking family members")
        
        // For testing purposes, trigger notification for mock family members
        // In real implementation, you'd need to correlate with incoming call info
        if !familyManager.familyMembers.isEmpty {
            let testMember = familyManager.familyMembers.first!
            print("CallMonitor: Testing with family member - \(testMember.name)")
            scheduleGentleNudgeNotification(for: testMember)
        }
    }
    
    // MARK: - Gentle Nudge Notification
    private func scheduleGentleNudgeNotification(for member: FamilyMember) {
        let content = UNMutableNotificationContent()
        content.title = "Digital Guardian"
        content.body = "Call with \(member.name). Remember your safe word if anything feels unsure."
        content.sound = nil // Silent notification
        content.categoryIdentifier = "FAMILY_CALL_REMINDER"
        
        // Add custom data for potential tap handling
        content.userInfo = [
            "familyMemberId": member.id,
            "familyMemberName": member.name,
            "safeWordQuestion": member.safeWordQuestion,
            "type": "gentle_nudge"
        ]
        
        // Schedule notification with 2-second delay
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 2.0, repeats: false)
        let request = UNNotificationRequest(
            identifier: "gentle_nudge_\(member.id)_\(Date().timeIntervalSince1970)",
            content: content,
            trigger: trigger
        )
        
        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("CallMonitor: Failed to schedule notification - \(error)")
            } else {
                print("CallMonitor: Gentle nudge scheduled for \(member.name)")
            }
        }
    }
    
    // MARK: - Public Methods
    func startMonitoring() {
        isMonitoring = true
        familyManager.loadFamilyMembers()
        print("CallMonitor: Monitoring started")
    }
    
    func stopMonitoring() {
        isMonitoring = false
        print("CallMonitor: Monitoring stopped")
    }
    
    // MARK: - Testing Methods
    func testGentleNudgeNotification(for member: FamilyMember) {
        print("CallMonitor: Testing notification for \(member.name)")
        scheduleGentleNudgeNotification(for: member)
    }
}

// MARK: - CXCallObserverDelegate
extension CallMonitor: CXCallObserverDelegate {
    func callObserver(_ callObserver: CXCallObserver, callChanged call: CXCall) {
        DispatchQueue.main.async {            
            if call.hasConnected && !call.hasEnded {
                self.lastCallStatus = "Call connected"
                self.handleCallConnected(call)
            } else if call.hasEnded {
                self.lastCallStatus = "Call ended"
            } else if call.isOutgoing {
                self.lastCallStatus = "Outgoing call"
            } else {
                self.lastCallStatus = "Incoming call"
            }
            
            print("CallMonitor: \(self.lastCallStatus)")
        }
    }
}

// MARK: - Notification Categories
extension CallMonitor {
    static func setupNotificationCategories() {
        // Define actions for the family call reminder
        let viewSafeWordAction = UNNotificationAction(
            identifier: "VIEW_SAFE_WORD",
            title: "View Safe Word Question",
            options: []
        )
        
        let callBackAction = UNNotificationAction(
            identifier: "SECURE_CALLBACK",
            title: "Secure Callback",
            options: []
        )
        
        // Create category
        let familyCallCategory = UNNotificationCategory(
            identifier: "FAMILY_CALL_REMINDER",
            actions: [viewSafeWordAction, callBackAction],
            intentIdentifiers: [],
            options: []
        )
        
        // Register with notification center
        UNUserNotificationCenter.current().setNotificationCategories([familyCallCategory])
    }
}
