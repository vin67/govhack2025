//
//  CallScreeningView.swift
//  GovHackAntiScam
//
//  Created by GovHack 2025 Team
//

import SwiftUI
import CallKit

struct CallScreeningView: View {
    @EnvironmentObject var contactService: ContactService
    @State private var isCallKitEnabled = false
    @State private var showingSettings = false
    @State private var recentScreenings: [Contact] = []
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                headerView
                
                callKitStatusView
                
                recentScreeningsView
                
                threatAnalyticsView
            }
            .padding()
        }
        .navigationTitle("Call Screening")
        .navigationBarTitleDisplayMode(.large)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Settings") {
                    showingSettings = true
                }
            }
        }
        .sheet(isPresented: $showingSettings) {
            CallScreeningSettingsView(isEnabled: $isCallKitEnabled)
        }
        .background(Color(.systemGroupedBackground).ignoresSafeArea())
        .onAppear {
            loadRecentScreenings()
            checkCallKitStatus()
        }
    }
    
    private var headerView: some View {
        VStack(spacing: 16) {
            Image(systemName: "phone.badge.checkmark")
                .font(.system(size: 50))
                .foregroundStyle(.green.gradient)
            
            Text("Real-time Call Protection")
                .font(.title2)
                .fontWeight(.bold)
            
            Text("Automatically screen incoming calls against our verified database")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(16)
    }
    
    private var callKitStatusView: some View {
        VStack(spacing: 16) {
            HStack {
                VStack(alignment: .leading) {
                    Text("CallKit Integration")
                        .font(.headline)
                    Text(isCallKitEnabled ? "Active - Screening calls" : "Inactive - Manual lookup only")
                        .font(.subheadline)
                        .foregroundColor(isCallKitEnabled ? .green : .orange)
                }
                
                Spacer()
                
                Image(systemName: isCallKitEnabled ? "checkmark.circle.fill" : "xmark.circle.fill")
                    .font(.title)
                    .foregroundColor(isCallKitEnabled ? .green : .red)
            }
            
            if !isCallKitEnabled {
                Button("Enable Call Screening") {
                    showingSettings = true
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(12)
            }
        }
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(16)
    }
    
    private var recentScreeningsView: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Recent Activity")
                .font(.headline)
                .padding(.horizontal)
            
            if recentScreenings.isEmpty {
                VStack(spacing: 12) {
                    Image(systemName: "phone.badge.plus")
                        .font(.system(size: 40))
                        .foregroundColor(.gray)
                    
                    Text("No recent call screenings")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    
                    Text("When CallKit is enabled, screened calls will appear here")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
                .padding(40)
                .background(Color(.secondarySystemGroupedBackground))
                .cornerRadius(16)
            } else {
                LazyVStack(spacing: 12) {
                    ForEach(recentScreenings.prefix(10)) { contact in
                        recentScreeningRow(contact)
                    }
                }
            }
        }
    }
    
    private func recentScreeningRow(_ contact: Contact) -> some View {
        HStack {
            Image(systemName: contact.riskLevel.icon)
                .font(.title2)
                .foregroundColor(contact.riskLevel.color)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(contact.formattedPhoneNumber)
                    .font(.headline)
                
                Text(contact.displayName)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text(contact.riskLevel.displayName)
                    .font(.caption)
                    .fontWeight(.medium)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(contact.riskLevel.color.opacity(0.2))
                    .foregroundColor(contact.riskLevel.color)
                    .cornerRadius(8)
                
                Text(contact.verifiedDate, style: .time)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(12)
    }
    
    private var threatAnalyticsView: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Threat Analytics")
                .font(.headline)
                .padding(.horizontal)
            
            HStack(spacing: 20) {
                analyticsCard(
                    title: "Blocked Today",
                    value: "0",
                    subtitle: "Scam calls",
                    color: .red,
                    icon: "phone.down.fill"
                )
                
                analyticsCard(
                    title: "Verified Today",
                    value: "0",
                    subtitle: "Safe calls",
                    color: .green,
                    icon: "checkmark.circle.fill"
                )
            }
        }
    }
    
    private func analyticsCard(title: String, value: String, subtitle: String, color: Color, icon: String) -> some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title)
                .foregroundColor(color)
            
            Text(value)
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(color)
            
            Text(title)
                .font(.caption)
                .fontWeight(.medium)
            
            Text(subtitle)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(12)
    }
    
    private func loadRecentScreenings() {
        recentScreenings = contactService.getRecentVerifications(limit: 10)
    }
    
    private func checkCallKitStatus() {
        // In a real implementation, check CallKit permissions and status
        isCallKitEnabled = false
    }
}

struct CallScreeningSettingsView: View {
    @Binding var isEnabled: Bool
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            List {
                Section {
                    Toggle("Enable Call Screening", isOn: $isEnabled)
                        .tint(.blue)
                } header: {
                    Text("CallKit Integration")
                } footer: {
                    Text("When enabled, incoming calls will be automatically checked against our verified database. Requires iOS permissions.")
                }
                
                Section("Privacy") {
                    Label("Data stays on device", systemImage: "lock.shield")
                        .foregroundColor(.green)
                    Label("No call content accessed", systemImage: "eye.slash")
                        .foregroundColor(.blue)
                }
            }
            .navigationTitle("Call Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    NavigationView {
        CallScreeningView()
            .environmentObject(ContactService.mock())
    }
}