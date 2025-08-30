//
//  VerificationView.swift
//  DigitalGuardianSimple
//
//  Universal verification for phone, email, and website
//

import SwiftUI

struct VerificationView: View {
    @StateObject private var dataManager = DataManager.shared
    @State private var inputText = ""
    @State private var selectedType = VerificationType.phone
    @State private var verificationResult: VerificationResult?
    @State private var isVerifying = false
    @Environment(\.dismiss) var dismiss
    
    enum VerificationType: String, CaseIterable {
        case phone = "Phone"
        case email = "Email"
        case website = "Website"
        
        var icon: String {
            switch self {
            case .phone: return "phone.fill"
            case .email: return "envelope.fill"
            case .website: return "globe"
            }
        }
        
        var placeholder: String {
            switch self {
            case .phone: return "1800 123 456"
            case .email: return "example@gov.au"
            case .website: return "www.example.gov.au"
            }
        }
        
        var keyboardType: UIKeyboardType {
            switch self {
            case .phone: return .phonePad
            case .email: return .emailAddress
            case .website: return .URL
            }
        }
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 12) {
                    Image(systemName: "magnifyingglass.circle.fill")
                        .font(.system(size: 60))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [.purple, .pink],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                    
                    Text("Verification Checker")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text("Check if a phone number, email, or website is safe")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding(.top)
                
                // Type Selector
                Picker("Verification Type", selection: $selectedType) {
                    ForEach(VerificationType.allCases, id: \.self) { type in
                        Label(type.rawValue, systemImage: type.icon)
                            .tag(type)
                    }
                }
                .pickerStyle(SegmentedPickerStyle())
                .padding(.horizontal)
                
                // Input Field
                VStack(alignment: .leading, spacing: 8) {
                    Label("Enter \(selectedType.rawValue)", systemImage: selectedType.icon)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    TextField(selectedType.placeholder, text: $inputText)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .keyboardType(selectedType.keyboardType)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                        .font(.title3)
                        .padding(.vertical, 8)
                }
                .padding(.horizontal)
                
                // Verify Button
                Button(action: verifyInput) {
                    HStack {
                        if isVerifying {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                .scaleEffect(0.8)
                        } else {
                            Image(systemName: "shield.checkered")
                            Text("Verify")
                                .fontWeight(.semibold)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(
                        LinearGradient(
                            colors: inputText.isEmpty ? [.gray] : [.purple, .pink],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .foregroundColor(.white)
                    .cornerRadius(12)
                }
                .disabled(inputText.isEmpty || isVerifying)
                .padding(.horizontal)
                
                // Result Display
                if let result = verificationResult {
                    ResultCard(result: result)
                        .padding(.horizontal)
                        .transition(.scale.combined(with: .opacity))
                }
                
                Spacer()
                
                // Info Footer
                VStack(spacing: 8) {
                    Label("Data source: Australian Government Services", systemImage: "info.circle")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    
                    if dataManager.isLoading {
                        ProgressView("Loading database...")
                            .font(.caption)
                    } else if !dataManager.contacts.isEmpty {
                        Text("\(dataManager.contacts.count) verified contacts in database")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.bottom)
            }
            .navigationBarTitle("", displayMode: .inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    private func verifyInput() {
        guard !inputText.isEmpty else { return }
        
        isVerifying = true
        verificationResult = nil
        
        // Simulate network delay for better UX
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            switch selectedType {
            case .phone:
                verificationResult = dataManager.verifyPhoneNumber(inputText)
            case .email:
                verificationResult = dataManager.verifyEmail(inputText)
            case .website:
                verificationResult = dataManager.verifyWebsite(inputText)
            }
            
            withAnimation(.spring()) {
                isVerifying = false
            }
        }
    }
}

// Result Card Component
struct ResultCard: View {
    let result: VerificationResult
    
    var backgroundColor: Color {
        if result.isSafe {
            return .green.opacity(0.1)
        } else if result.isThreat {
            return .red.opacity(0.1)
        } else {
            return .orange.opacity(0.1)
        }
    }
    
    var borderColor: Color {
        if result.isSafe {
            return .green
        } else if result.isThreat {
            return .red
        } else {
            return .orange
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Status Header
            HStack {
                Image(systemName: result.isSafe ? "checkmark.shield.fill" :
                                 result.isThreat ? "exclamationmark.shield.fill" :
                                 "questionmark.shield.fill")
                    .font(.title2)
                    .foregroundColor(borderColor)
                
                Text(result.riskLevel.uppercased())
                    .font(.headline)
                    .foregroundColor(borderColor)
                
                Spacer()
                
                if result.confidenceScore > 0 {
                    Text("\(Int(result.confidenceScore * 100))% confidence")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            // Message
            Text(result.message)
                .font(.subheadline)
                .foregroundColor(.primary)
                .fixedSize(horizontal: false, vertical: true)
            
            // Organization Details
            if result.isVerified && !result.organizationName.isEmpty && result.organizationName != "Unknown" {
                Divider()
                
                VStack(alignment: .leading, spacing: 6) {
                    DetailRow(label: "Organization", value: result.organizationName)
                    DetailRow(label: "Type", value: result.organizationType.capitalized)
                    if !result.services.isEmpty && result.services != "nan" {
                        DetailRow(label: "Services", value: result.services)
                    }
                }
                .font(.caption)
            }
        }
        .padding()
        .background(backgroundColor)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(borderColor, lineWidth: 2)
        )
        .cornerRadius(12)
    }
}

// Detail Row Component
struct DetailRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack(alignment: .top) {
            Text("\(label):")
                .fontWeight(.medium)
                .foregroundColor(.secondary)
            Text(value)
                .foregroundColor(.primary)
            Spacer()
        }
    }
}

#Preview {
    VerificationView()
}
