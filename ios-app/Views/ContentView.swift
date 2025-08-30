//
//  ContentView.swift
//  GovHackAntiScam
//
//  Created by GovHack 2025 Team
//

import SwiftUI

struct ContentView: View {
    @StateObject private var contactService = ContactService()
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            NavigationView {
                ContactLookupView()
                    .environmentObject(contactService)
            }
            .tabItem {
                Image(systemName: "magnifyingglass.circle.fill")
                Text("Lookup")
            }
            .tag(0)
            
            NavigationView {
                CallScreeningView()
                    .environmentObject(contactService)
            }
            .tabItem {
                Image(systemName: "phone.badge.checkmark")
                Text("Screen")
            }
            .tag(1)
            
            NavigationView {
                ContactListView()
                    .environmentObject(contactService)
            }
            .tabItem {
                Image(systemName: "list.bullet.clipboard.fill")
                Text("Directory")
            }
            .tag(2)
            
            NavigationView {
                DashboardView()
                    .environmentObject(contactService)
            }
            .tabItem {
                Image(systemName: "chart.bar.fill")
                Text("Dashboard")
            }
            .tag(3)
        }
        .accentColor(.blue)
    }
}

#Preview {
    ContentView()
}