//
//  LLMQueryView.swift
//  DigitalGuardianSimple
//
//  LLM Query Interface for Digital Guardian - GovHack 2025
//

import SwiftUI

struct LLMQueryView: View {
    @Environment(\.presentationMode) var presentationMode
    @StateObject private var llmService = LLMService()
    @State private var queryText: String = ""
    @State private var response: String = ""
    @State private var isLoading: Bool = false
    @State private var showingResponse: Bool = false
    
    // Sample queries to help users get started
    private let sampleQueries = [
        "What is the ATO phone number?",
        "Call Medicare",
        "Hospital emergency contacts",
        "Centrelink phone number",
        "What services help with taxes?"
    ]
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Header
                VStack(spacing: 12) {
                    Image(systemName: "bubble.left.and.text.bubble.right.fill")
                        .font(.system(size: 50))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [.orange, .red],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                    
                    Text("Ask Digital Guardian")
                        .font(.title)
                        .fontWeight(.bold)
                    
                    Text("Find verified government contact information")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding(.top)
                
                Divider()
                
                // Query Input Section
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Image(systemName: "questionmark.circle.fill")
                            .foregroundColor(.orange)
                        Text("Your Question")
                            .font(.headline)
                            .fontWeight(.medium)
                    }
                    
                    TextField("Ask about government services...", text: $queryText, axis: .vertical)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .lineLimit(3...6)
                        .font(.body)
                    
                    Text("💡 Examples: \"ATO phone number\", \"Call Medicare\", \"Hospital contacts\"")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(.horizontal)
                
                // Sample Queries
                if queryText.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Image(systemName: "lightbulb.fill")
                                .foregroundColor(.yellow)
                            Text("Try these questions:")
                                .font(.subheadline)
                                .fontWeight(.medium)
                        }
                        .padding(.horizontal)
                        
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 12) {
                                ForEach(sampleQueries, id: \.self) { query in
                                    Button(query) {
                                        queryText = query
                                    }
                                    .font(.caption)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 8)
                                    .background(Color.orange.opacity(0.1))
                                    .foregroundColor(.orange)
                                    .cornerRadius(16)
                                }
                            }
                            .padding(.horizontal)
                        }
                    }
                }
                
                // Ask Button
                Button(action: askDigitalGuardian) {
                    HStack {
                        if isLoading {
                            ProgressView()
                                .scaleEffect(0.8)
                                .foregroundColor(.white)
                        } else {
                            Image(systemName: "paperplane.fill") 
                        }
                        Text(isLoading ? "Asking..." : "Ask Digital Guardian")
                            .fontWeight(.semibold)
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(queryText.isEmpty ? Color.gray : Color.orange)
                    .cornerRadius(12)
                    .shadow(color: .orange.opacity(0.3), radius: 5, x: 0, y: 3)
                }
                .disabled(queryText.isEmpty || isLoading)
                .padding(.horizontal)
                
                // Response Section
                if showingResponse {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: "shield.checkered")
                                .foregroundColor(.blue)
                            Text("Digital Guardian Response")
                                .font(.headline)
                                .fontWeight(.medium)
                        }
                        
                        ScrollView {
                            Text(response)
                                .font(.body)
                                .padding()
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color(.secondarySystemBackground))
                                .cornerRadius(12)
                        }
                        .frame(maxHeight: 200)
                    }
                    .padding(.horizontal)
                }
                
                Spacer()
                
                // Footer
                Text("🤖 OpenELM-270M on Apple Neural Engine • 383 verified contacts • GovHack 2025")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.bottom, 8)
            }
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarBackButtonHidden(true)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
            }
        }
    }
    
    private func askDigitalGuardian() {
        guard !queryText.isEmpty else { return }
        
        isLoading = true
        showingResponse = false
        
        Task {
            let llmResponse = await llmService.processQuery(queryText)
            
            await MainActor.run {
                response = llmResponse
                isLoading = false
                showingResponse = true
            }
        }
    }
}

#Preview {
    LLMQueryView()
}
