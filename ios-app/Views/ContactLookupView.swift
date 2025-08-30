//
//  ContactLookupView.swift
//  GovHackAntiScam
//
//  Created by GovHack 2025 Team
//

import SwiftUI

struct ContactLookupView: View {
    @EnvironmentObject var contactService: ContactService
    @State private var phoneNumber = ""
    @State private var verificationResult: ScamResult?
    @State private var showingResult = false
    
    var body: some View {
        VStack(spacing: 24) {
            headerView
            
            searchSection
            
            if showingResult, let result = verificationResult {
                resultView(result)
                    .transition(.scale.combined(with(.opacity))
            }
            
            Spacer()
            
            quickStatsView
        }
        .padding()
        .navigationTitle("Scam Lookup")
        .background(Color(.systemGroupedBackground).ignoresSafeArea())
    }
    
    private var headerView: some View {
        VStack(spacing: 16) {
            Image(systemName: "shield.checkered")
                .font(.system(size: 60))
                .foregroundStyle(.blue.gradient)
            
            Text("Verify Contact Safety")
                .font(.title)
                .fontWeight(.bold)
            
            Text("Enter a phone number to check if it's verified safe or a known threat")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding()
    }
    
    private var searchSection: some View {
        VStack(spacing: 16) {
            HStack {
                Image(systemName: "phone.fill")
                    .foregroundColor(.blue)
                    .font(.title2)
                
                TextField("Enter phone number", text: $phoneNumber)
                    .keyboardType(.phonePad)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .onSubmit {
                        verifyNumber()
                    }
            }
            
            Button(action: verifyNumber) {
                HStack {
                    Image(systemName: "magnifyingglass")
                    Text("Verify Number")
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(phoneNumber.isEmpty ? Color.gray : Color.blue)
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            .disabled(phoneNumber.isEmpty)
            .animation(.easeInOut(duration: 0.2), value: phoneNumber.isEmpty)
        }
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(16)
    }
    
    private func resultView(_ result: ScamResult) -> some View {
        VStack(spacing: 16) {
            HStack {
                Image(systemName: result.isScam ? "exclamationmark.triangle.fill" : 
                      result.alertMessage.contains("Verified") ? "checkmark.shield.fill" : "questionmark.shield.fill")
                    .font(.system(size: 40))
                    .foregroundColor(result.alertColor)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(result.alertMessage)
                        .font(.headline)
                        .fontWeight(.semibold)
                    
                    switch result {
                    case .verified(let contact):
                        Text("Organization: \(contact.organizationName)")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        Text("Type: \(contact.organizationType.displayName)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    case .threat(let contact):
                        Text("⚠️ Do not answer this call")
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .foregroundColor(.red)
                        if !contact.notes.isEmpty {
                            Text(contact.notes)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    case .unknown:
                        Text("Exercise caution with unknown numbers")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
            }
            .padding()
            .background(result.alertColor.opacity(0.1))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(result.alertColor.opacity(0.3), lineWidth: 1)
            )
        }
    }
    
    private var quickStatsView: some View {
        HStack(spacing: 20) {
            statView(title: "Safe Contacts", value: "\(contactService.totalContacts)", color: .green)
            statView(title: "Threats", value: "\(contactService.totalThreats)", color: .red)
            statView(title: "Safety Rate", value: String(format: "%.1f%%", contactService.safetyRate), color: .blue)
        }
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(16)
    }
    
    private func statView(title: String, value: String, color: Color) -> some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(color)
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
    
    private func verifyNumber() {
        let result = contactService.verifyContact(phoneNumber: phoneNumber)
        verificationResult = result
        showingResult = true
        
        // Add haptic feedback
        if result.isScam {
            let impactFeedback = UIImpactFeedbackGenerator(style: .heavy)
            impactFeedback.impactOccurred()
        } else {
            let impactFeedback = UIImpactFeedbackGenerator(style: .light)
            impactFeedback.impactOccurred()
        }
    }
}

#Preview {
    NavigationView {
        ContactLookupView()
            .environmentObject(ContactService.mock())
    }
}