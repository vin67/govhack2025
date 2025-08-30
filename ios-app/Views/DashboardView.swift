//
//  DashboardView.swift
//  GovHackAntiScam
//
//  Created by GovHack 2025 Team
//

import SwiftUI
import Charts

struct DashboardView: View {
    @EnvironmentObject var contactService: ContactService
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                headerView
                
                quickStatsGrid
                
                categoryChartView
                
                stateDistributionView
                
                recentActivityView
            }
            .padding()
        }
        .navigationTitle("Dashboard")
        .navigationBarTitleDisplayMode(.large)
        .refreshable {
            contactService.loadContacts()
        }
        .background(Color(.systemGroupedBackground).ignoresSafeArea())
    }
    
    private var headerView: some View {
        VStack(spacing: 12) {
            HStack {
                Image(systemName: "chart.bar.fill")
                    .font(.title)
                    .foregroundColor(.blue)
                
                VStack(alignment: .leading) {
                    Text("Anti-Scam Analytics")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    if let lastUpdated = contactService.lastUpdated {
                        Text("Updated \(lastUpdated, style: .relative) ago")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
            }
            
            safetyRateView
        }
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(16)
    }
    
    private var safetyRateView: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Overall Safety Rate")
                    .font(.headline)
                
                Text(String(format: "%.1f%% of contacts verified safe", contactService.safetyRate))
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            ZStack {
                Circle()
                    .stroke(Color.gray.opacity(0.3), lineWidth: 8)
                    .frame(width: 60, height: 60)
                
                Circle()
                    .trim(from: 0.0, to: contactService.safetyRate / 100.0)
                    .stroke(safetyRateColor, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                    .frame(width: 60, height: 60)
                    .rotationEffect(.degrees(-90))
                    .animation(.easeInOut(duration: 1.0), value: contactService.safetyRate)
                
                Text("\(Int(contactService.safetyRate))%")
                    .font(.caption)
                    .fontWeight(.bold)
                    .foregroundColor(safetyRateColor)
            }
        }
    }
    
    private var safetyRateColor: Color {
        switch contactService.safetyRate {
        case 80...100: return .green
        case 60..<80: return .orange
        default: return .red
        }
    }
    
    private var quickStatsGrid: some View {
        LazyVGrid(columns: [
            GridItem(.flexible()),
            GridItem(.flexible())
        ], spacing: 16) {
            statCard(
                title: "Total Contacts",
                value: "\(contactService.totalContacts)",
                subtitle: "Verified entries",
                color: .blue,
                icon: "person.3.fill"
            )
            
            statCard(
                title: "Safe Contacts",
                value: "\(contactService.verifiedContacts)",
                subtitle: "Government verified",
                color: .green,
                icon: "checkmark.shield.fill"
            )
            
            statCard(
                title: "Known Threats",
                value: "\(contactService.totalThreats)",
                subtitle: "Scam indicators",
                color: .red,
                icon: "exclamationmark.triangle.fill"
            )
            
            statCard(
                title: "Protection Level",
                value: contactService.safetyRate >= 80 ? "High" : contactService.safetyRate >= 60 ? "Medium" : "Low",
                subtitle: "Current status",
                color: safetyRateColor,
                icon: "shield.fill"
            )
        }
    }
    
    private func statCard(title: String, value: String, subtitle: String, color: Color, icon: String) -> some View {
        VStack(spacing: 12) {
            Image(systemName: icon)
                .font(.title)
                .foregroundColor(color)
            
            VStack(spacing: 4) {
                Text(value)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(color)
                
                Text(title)
                    .font(.caption)
                    .fontWeight(.medium)
                
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.secondarySystemGroupedBackground))
        .cornerRadius(12)
    }
    
    private var categoryChartView: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Contacts by Category")
                .font(.headline)
                .padding(.horizontal)
            
            let categoryStats = contactService.getStatsByCategory()
            
            if !categoryStats.isEmpty {
                VStack(spacing: 8) {
                    ForEach(Array(categoryStats.keys.sorted(by: { categoryStats[$0]! > categoryStats[$1]! })), id: \.self) { category in
                        categoryBar(category: category, count: categoryStats[category] ?? 0, total: contactService.totalContacts)
                    }
                }
                .padding()
                .background(Color(.secondarySystemGroupedBackground))
                .cornerRadius(12)
            } else {
                Text("No data available")
                    .foregroundColor(.secondary)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color(.secondarySystemGroupedBackground))
                    .cornerRadius(12)
            }
        }
    }
    
    private func categoryBar(category: ContactCategory, count: Int, total: Int) -> some View {
        VStack(spacing: 4) {
            HStack {
                Label(category.shortName, systemImage: category.icon)
                    .font(.caption)
                    .foregroundColor(category.color)
                
                Spacer()
                
                Text("\(count)")
                    .font(.caption)
                    .fontWeight(.medium)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                        .frame(height: 6)
                        .cornerRadius(3)
                    
                    Rectangle()
                        .fill(category.color)
                        .frame(width: geometry.size.width * (total > 0 ? Double(count) / Double(total) : 0), height: 6)
                        .cornerRadius(3)
                        .animation(.easeInOut(duration: 0.8), value: count)
                }
            }
            .frame(height: 6)
        }
    }
    
    private var stateDistributionView: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Geographic Distribution")
                .font(.headline)
                .padding(.horizontal)
            
            let stateStats = contactService.getStatsByState()
            let topStates = Array(stateStats.sorted { $0.value > $1.value }.prefix(5))
            
            if !topStates.isEmpty {
                VStack(spacing: 8) {
                    ForEach(topStates, id: \.key) { state, count in
                        stateRow(state: state, count: count)
                    }
                }
                .padding()
                .background(Color(.secondarySystemGroupedBackground))
                .cornerRadius(12)
            } else {
                Text("No geographic data available")
                    .foregroundColor(.secondary)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color(.secondarySystemGroupedBackground))
                    .cornerRadius(12)
            }
        }
    }
    
    private func stateRow(state: String, count: Int) -> some View {
        HStack {
            Text(state == "Federal" ? "🇦🇺" : "🏛️")
                .font(.title3)
            
            Text(state)
                .font(.body)
                .fontWeight(.medium)
            
            Spacer()
            
            Text("\(count)")
                .font(.body)
                .fontWeight(.medium)
                .foregroundColor(.blue)
        }
    }
    
    private var recentActivityView: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Recent Verifications")
                .font(.headline)
                .padding(.horizontal)
            
            let recentContacts = contactService.getRecentVerifications(limit: 5)
            
            if !recentContacts.isEmpty {
                VStack(spacing: 8) {
                    ForEach(recentContacts) { contact in
                        recentActivityRow(contact: contact)
                    }
                }
                .padding()
                .background(Color(.secondarySystemGroupedBackground))
                .cornerRadius(12)
            } else {
                Text("No recent activity")
                    .foregroundColor(.secondary)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color(.secondarySystemGroupedBackground))
                    .cornerRadius(12)
            }
        }
    }
    
    private func recentActivityRow(contact: Contact) -> some View {
        HStack {
            Image(systemName: contact.organizationType.icon)
                .font(.title3)
                .foregroundColor(contact.organizationType.color)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(contact.displayName)
                    .font(.body)
                    .fontWeight(.medium)
                    .lineLimit(1)
                
                Text(contact.organizationType.displayName)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 2) {
                Image(systemName: contact.riskLevel.icon)
                    .font(.caption)
                    .foregroundColor(contact.riskLevel.color)
                
                Text(contact.verifiedDate, style: .time)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }
}

#Preview {
    NavigationView {
        DashboardView()
            .environmentObject(ContactService.mock())
    }
}