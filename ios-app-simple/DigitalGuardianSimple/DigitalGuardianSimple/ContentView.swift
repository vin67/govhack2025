//
//  ContentView.swift
//  DigitalGuardianSimple
//
//  Digital Guardian with Navigation - Anti-Scam Protection for GovHack 2025
//

import SwiftUI

struct ContentView: View {
    @State private var showingAlert = false
    @State private var showingVerification = false
    @State private var showingFamilyCircle = false
    
    var body: some View {
        TabView {
            HomeView(showingAlert: $showingAlert, showingVerification: $showingVerification, showingFamilyCircle: $showingFamilyCircle)
                .tabItem {
                    Image(systemName: "shield.checkered")
                    Text("Protection")
                }
            
            FamilyCircleView()
                .tabItem {
                    Image(systemName: "person.3.sequence.fill")
                    Text("Family Circle")
                }
        }
    }
}

struct HomeView: View {
    @Binding var showingAlert: Bool
    @Binding var showingVerification: Bool
    @Binding var showingFamilyCircle: Bool
    
    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Header Section
                VStack(spacing: 16) {
                    // Shield icon with gradient
                    Image(systemName: "shield.checkered")
                        .font(.system(size: 80))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [.blue, .cyan],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .shadow(color: .blue.opacity(0.3), radius: 10, x: 0, y: 5)
                    
                    // App title
                    Text("Digital Guardian")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.primary)
                    
                    // Subtitle
                    Text("Your Shield Against Scams")
                        .font(.headline)
                        .foregroundColor(.secondary)
                    
                    // GovHack badge
                    HStack {
                        Image(systemName: "trophy.fill")
                            .foregroundColor(.orange)
                        Text("GovHack 2025")
                            .font(.caption)
                            .fontWeight(.medium)
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(.orange.opacity(0.1))
                    .cornerRadius(20)
                }
                .padding(.top, 20)
                
                Spacer()
                
                // Feature Cards
                VStack(spacing: 16) {
                    FeatureCard(
                        icon: "message.badge.filled.fill",
                        title: "SMS Protection",
                        description: "Analyze suspicious messages",
                        color: .green,
                        action: {
                            // TODO: Implement SMS sharing
                        }
                    )
                    
                    FeatureCard(
                        icon: "person.3.sequence.fill",
                        title: "Family Circle",
                        description: "Safe word protection for family",
                        color: .purple,
                        action: {
                            showingFamilyCircle = true
                        }
                    )
                    
                    FeatureCard(
                        icon: "phone.badge.checkmark",
                        title: "Call Screening",
                        description: "Identify scam calls instantly",
                        color: .blue,
                        action: {
                            // TODO: Implement call screening
                        }
                    )
                    
                    // Clickable Number Checker
                    Button(action: {
                        showingVerification = true
                    }) {
                        HStack(spacing: 16) {
                            Image(systemName: "magnifyingglass.circle.fill")
                                .font(.system(size: 30))
                                .foregroundColor(.purple)
                                .frame(width: 50, height: 50)
                                .background(Color.purple.opacity(0.1))
                                .cornerRadius(10)
                            
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Verification Checker")
                                    .font(.headline)
                                    .foregroundColor(.primary)
                                Text("Check phone, email, or website")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            
                            Spacer()
                            
                            Image(systemName: "chevron.right")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .padding()
                        .background(Color(.secondarySystemBackground))
                        .cornerRadius(12)
                    }
                    .buttonStyle(PlainButtonStyle())
                }
                .padding(.horizontal)
                
                Spacer()
                
                // Action Button
                Button(action: {
                    showingAlert = true
                }) {
                    HStack {
                        Image(systemName: "checkmark.shield")
                        Text("Start Protection")
                            .fontWeight(.semibold)
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(
                        LinearGradient(
                            colors: [.blue, .cyan],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .cornerRadius(12)
                    .shadow(color: .blue.opacity(0.3), radius: 5, x: 0, y: 3)
                }
                .padding(.horizontal)
                .alert("Digital Guardian Active", isPresented: $showingAlert) {
                    Button("OK", role: .cancel) { }
                } message: {
                    Text("You're now protected against scams! Built with Claude AI assistance.")
                }
                
                // Footer
                Text("Built with Claude for GovHack 2025")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .padding(.bottom, 8)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color(.systemBackground))
            .navigationBarHidden(true)
            .sheet(isPresented: $showingVerification) {
                VerificationView()
            }
            .sheet(isPresented: $showingFamilyCircle) {
                FamilyCircleView()
            }
        }
    }
}

// Feature Card Component
struct FeatureCard: View {
    let icon: String
    let title: String
    let description: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 16) {
                Image(systemName: icon)
                    .font(.system(size: 30))
                    .foregroundColor(color)
                    .frame(width: 50, height: 50)
                    .background(color.opacity(0.1))
                    .cornerRadius(10)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.headline)
                        .foregroundColor(.primary)
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.secondarySystemBackground))
            .cornerRadius(12)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

#Preview {
    ContentView()
}