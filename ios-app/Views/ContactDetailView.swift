//
//  ContactDetailView.swift
//  GovHackAntiScam
//
//  Created by GovHack 2025 Team
//

import SwiftUI

struct ContactDetailView: View {
    let contact: Contact
    @State private var showingShareSheet = false
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                headerView
                
                contactInfoSection
                
                verificationSection
                
                organizationSection
                
                if !contact.notes.isEmpty {
                    notesSection
                }
            }
            .padding()
        }
        .navigationTitle(contact.displayName)
        .navigationBarTitleDisplayMode(.large)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Share") {
                    showingShareSheet = true
                }
            }
        }
        .sheet(isPresented: $showingShareSheet) {
            ShareSheet(contact: contact)
        }
        .background(Color(.systemGroupedBackground).ignoresSafeArea())
    }
    
    private var headerView: some View {
        VStack(spacing: 16) {
            Image(systemName: contact.organizationType.icon)
                .font(.system(size: 60))
                .foregroundColor(contact.organizationType.color)
                .padding()
                .background(contact.organizationType.color.opacity(0.1))
                .clipShape(Circle())
            
            VStack(spacing: 8) {
                Text(contact.organizationName)
                    .font(.title2)
                    .fontWeight(.bold)
                    .multilineTextAlignment(.center)
                
                HStack(spacing: 12) {
                    Label(contact.riskLevel.displayName, systemImage: contact.riskLevel.icon)
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(contact.riskLevel.color.opacity(0.2))
                        .foregroundColor(contact.riskLevel.color)
                        .cornerRadius(20)
                    
                    Label(contact.organizationType.displayName, systemImage: contact.organizationType.icon)
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(contact.organizationType.color.opacity(0.2))
                        .foregroundColor(contact.organizationType.color)
                        .cornerRadius(20)
                }
            }
        }
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(16)
    }
    
    private var contactInfoSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Contact Information")
                .font(.headline)
                .padding(.horizontal)
            
            VStack(spacing: 12) {
                contactInfoRow(
                    icon: contact.type.icon,
                    label: contact.type.displayName,
                    value: contact.type == .phone ? contact.formattedPhoneNumber : contact.value,
                    isCallable: contact.type == .phone
                )
                
                if contact.state != "Unknown" {
                    contactInfoRow(
                        icon: "location.fill",
                        label: "Region",
                        value: contact.state,
                        isCallable: false
                    )
                }
                
                contactInfoRow(
                    icon: "folder.fill",
                    label: "Category",
                    value: contact.category.rawValue,
                    isCallable: false
                )
            }
        }
    }
    
    private func contactInfoRow(icon: String, label: String, value: String, isCallable: Bool) -> some View {
        HStack(spacing: 16) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.blue)
                .frame(width: 30)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(label)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text(value)
                    .font(.body)
                    .fontWeight(.medium)
            }
            
            Spacer()
            
            if isCallable && contact.type == .phone {
                Button(action: callNumber) {
                    Image(systemName: "phone.fill")
                        .font(.title3)
                        .foregroundColor(.green)
                }
                .buttonStyle(.borderless)
            }
        }
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(12)
    }
    
    private var verificationSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Verification Details")
                .font(.headline)
                .padding(.horizontal)
            
            VStack(spacing: 12) {
                verificationRow(
                    icon: "checkmark.seal.fill",
                    label: "Confidence Score",
                    value: String(format: "%.0f%%", contact.confidenceScore * 100),
                    color: confidenceColor
                )
                
                verificationRow(
                    icon: "calendar",
                    label: "Verified Date",
                    value: DateFormatter.userFriendly.string(from: contact.verifiedDate),
                    color: .blue
                )
                
                verificationRow(
                    icon: "server.rack",
                    label: "Source Agent",
                    value: contact.sourceAgent.replacingOccurrences(of: "_", with: " ").capitalized,
                    color: .purple
                )
            }
        }
    }
    
    private func verificationRow(icon: String, label: String, value: String, color: Color) -> some View {
        HStack(spacing: 16) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
                .frame(width: 30)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(label)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text(value)
                    .font(.body)
                    .fontWeight(.medium)
            }
            
            Spacer()
        }
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(12)
    }
    
    private var organizationSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Organization")
                .font(.headline)
                .padding(.horizontal)
            
            VStack(spacing: 12) {
                HStack(spacing: 16) {
                    Image(systemName: contact.organizationType.icon)
                        .font(.title)
                        .foregroundColor(contact.organizationType.color)
                        .frame(width: 40, height: 40)
                        .background(contact.organizationType.color.opacity(0.2))
                        .clipShape(Circle())
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(contact.organizationType.displayName)
                            .font(.headline)
                            .fontWeight(.semibold)
                        
                        Text(contact.riskLevel.description)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                }
                .padding()
                .background(Color(.secondarySystemGroupedBackground))
                .cornerRadius(12)
            }
        }
    }
    
    private var notesSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Additional Notes")
                .font(.headline)
                .padding(.horizontal)
            
            Text(contact.notes)
                .font(.body)
                .padding()
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color(.secondarySystemGroupedBackground))
                .cornerRadius(12)
        }
    }
    
    private var confidenceColor: Color {
        switch contact.confidenceScore {
        case 0.8...1.0: return .green
        case 0.6..<0.8: return .orange
        default: return .red
        }
    }
    
    private func callNumber() {
        guard contact.type == .phone,
              let url = URL(string: "tel:\(contact.value.replacingOccurrences(of: " ", with: ""))") else {
            return
        }
        
        if UIApplication.shared.canOpenURL(url) {
            UIApplication.shared.open(url)
        }
    }
}

struct ShareSheet: View {
    let contact: Contact
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Share Contact")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Text(shareText)
                    .padding()
                    .background(Color(.secondarySystemGroupedBackground))
                    .cornerRadius(12)
                    .font(.body)
                
                Button("Copy to Clipboard") {
                    UIPasteboard.general.string = shareText
                    dismiss()
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(12)
                
                Spacer()
            }
            .padding()
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    private var shareText: String {
        """
        Verified Contact Information
        
        Organization: \(contact.organizationName)
        Contact: \(contact.formattedPhoneNumber)
        Type: \(contact.organizationType.displayName)
        Status: \(contact.riskLevel.displayName)
        Region: \(contact.state)
        
        Verified by GovHack 2025 Anti-Scam System
        Confidence: \(String(format: "%.0f%%", contact.confidenceScore * 100))
        """
    }
}

extension DateFormatter {
    static let userFriendly: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        return formatter
    }()
}

#Preview {
    NavigationView {
        ContactDetailView(contact: Contact.mockData().first!)
    }
}