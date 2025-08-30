//
//  ContactListView.swift
//  GovHackAntiScam
//
//  Created by GovHack 2025 Team
//

import SwiftUI

struct ContactListView: View {
    @EnvironmentObject var contactService: ContactService
    @State private var searchText = ""
    @State private var selectedCategory: ContactCategory?
    @State private var selectedState: String = "All"
    @State private var showingFilters = false
    
    private var filteredContacts: [Contact] {
        var contacts = contactService.searchContacts(query: searchText)
        
        if let category = selectedCategory {
            contacts = contacts.filter { $0.category == category }
        }
        
        if selectedState != "All" {
            contacts = contactService.getContactsByState(selectedState)
        }
        
        return contacts
    }
    
    private var availableStates: [String] {
        let states = Array(Set(contactService.contacts.map(\.state))).sorted()
        return ["All"] + states
    }
    
    var body: some View {
        VStack {
            if contactService.isLoading {
                loadingView
            } else {
                contactListView
            }
        }
        .navigationTitle("Contact Directory")
        .searchable(text: $searchText, prompt: "Search contacts...")
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Filter") {
                    showingFilters = true
                }
            }
        }
        .sheet(isPresented: $showingFilters) {
            FilterView(
                selectedCategory: $selectedCategory,
                selectedState: $selectedState,
                availableStates: availableStates
            )
        }
        .refreshable {
            contactService.loadContacts()
        }
    }
    
    private var loadingView: some View {
        VStack(spacing: 20) {
            ProgressView()
                .scaleEffect(1.2)
            
            Text("Loading verified contacts...")
                .font(.headline)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private var contactListView: some View {
        List {
            if !filteredContacts.isEmpty {
                statsSection
                
                contactsSection
            } else {
                emptyStateView
            }
        }
        .listStyle(InsetGroupedListStyle())
    }
    
    private var statsSection: some View {
        Section {
            HStack(spacing: 20) {
                statItem(title: "Total", value: contactService.totalContacts, color: .blue)
                statItem(title: "Safe", value: contactService.verifiedContacts, color: .green)
                statItem(title: "Threats", value: contactService.totalThreats, color: .red)
            }
            .padding(.vertical, 8)
        }
    }
    
    private func statItem(title: String, value: Int, color: Color) -> some View {
        VStack(spacing: 4) {
            Text("\(value)")
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(color)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
    
    private var contactsSection: some View {
        Section {
            ForEach(filteredContacts) { contact in
                NavigationLink(destination: ContactDetailView(contact: contact)) {
                    ContactRow(contact: contact)
                }
            }
        } header: {
            Text("Verified Contacts (\(filteredContacts.count))")
        } footer: {
            if let lastUpdated = contactService.lastUpdated {
                Text("Last updated: \(lastUpdated, formatter: dateFormatter)")
                    .font(.caption)
            }
        }
    }
    
    private var emptyStateView: some View {
        Section {
            VStack(spacing: 16) {
                Image(systemName: "magnifyingglass")
                    .font(.system(size: 50))
                    .foregroundColor(.gray)
                
                Text("No contacts found")
                    .font(.headline)
                    .foregroundColor(.primary)
                
                Text("Try adjusting your search or filters")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                
                Button("Clear Filters") {
                    searchText = ""
                    selectedCategory = nil
                    selectedState = "All"
                }
                .buttonStyle(.bordered)
            }
            .frame(maxWidth: .infinity)
            .padding(40)
        }
    }
    
    private let dateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter
    }()
}

struct ContactRow: View {
    let contact: Contact
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: contact.organizationType.icon)
                .font(.title2)
                .foregroundColor(contact.organizationType.color)
                .frame(width: 30)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(contact.displayName)
                    .font(.headline)
                    .lineLimit(1)
                
                HStack(spacing: 8) {
                    Text(contact.organizationType.displayName)
                        .font(.caption)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(contact.organizationType.color.opacity(0.2))
                        .foregroundColor(contact.organizationType.color)
                        .cornerRadius(4)
                    
                    Text(contact.state)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                if contact.type == .phone {
                    Text(contact.formattedPhoneNumber)
                        .font(.subheadline)
                        .foregroundColor(.blue)
                } else {
                    Text(contact.value)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Image(systemName: contact.riskLevel.icon)
                    .font(.title3)
                    .foregroundColor(contact.riskLevel.color)
                
                Text(String(format: "%.0f%%", contact.confidenceScore * 100))
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 4)
    }
}

struct FilterView: View {
    @Binding var selectedCategory: ContactCategory?
    @Binding var selectedState: String
    let availableStates: [String]
    
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            List {
                Section("Category") {
                    Picker("Category", selection: $selectedCategory) {
                        Text("All Categories").tag(nil as ContactCategory?)
                        ForEach(ContactCategory.allCases, id: \.self) { category in
                            Label(category.rawValue, systemImage: category.icon)
                                .tag(category as ContactCategory?)
                        }
                    }
                    .pickerStyle(.menu)
                }
                
                Section("State/Region") {
                    Picker("State", selection: $selectedState) {
                        ForEach(availableStates, id: \.self) { state in
                            Text(state).tag(state)
                        }
                    }
                    .pickerStyle(.menu)
                }
                
                Section {
                    Button("Clear All Filters") {
                        selectedCategory = nil
                        selectedState = "All"
                    }
                    .foregroundColor(.red)
                }
            }
            .navigationTitle("Filter Contacts")
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
        ContactListView()
            .environmentObject(ContactService.mock())
    }
}