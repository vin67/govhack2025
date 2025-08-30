//
//  DigitalGuardianSimpleApp.swift
//  DigitalGuardianSimple
//
//  Created by Vinod Ralh on 30/8/2025.
//

import SwiftUI
import UserNotifications

@main
struct DigitalGuardianSimpleApp: App {
    @StateObject private var callMonitor = CallMonitor()
    @StateObject private var notificationHandler = NotificationHandler()
    
    init() {
        // Setup notification categories
        CallMonitor.setupNotificationCategories()
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(callMonitor)
                .environmentObject(notificationHandler)
                .onAppear {
                    callMonitor.startMonitoring()
                }
        }
    }
}
