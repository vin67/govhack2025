import SwiftUI

struct FamilyCircleView: View {
    @StateObject private var familyManager = FamilyCircleManager()
    @EnvironmentObject var callMonitor: CallMonitor
    @State private var showingAddMember = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Header
                VStack(spacing: 12) {
                    Image(systemName: "person.3.sequence.fill")
                        .font(.system(size: 60))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [.purple, .pink],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                    
                    Text("Family Circle")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    
                    Text("Protect your loved ones with safe word verification")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding(.top)
                
                // Family Members List
                if familyManager.familyMembers.isEmpty {
                    // Empty State
                    VStack(spacing: 16) {
                        Image(systemName: "person.badge.plus")
                            .font(.system(size: 40))
                            .foregroundColor(.gray)
                        
                        Text("No family members added")
                            .font(.headline)
                            .foregroundColor(.secondary)
                        
                        Text("Add your family members to enable safe word protection during calls")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                    .padding(.vertical, 40)
                } else {
                    // Family Members List
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(familyManager.familyMembers) { member in
                                FamilyMemberCard(member: member) {
                                    familyManager.removeFamilyMember(member)
                                }
                            }
                        }
                        .padding(.horizontal)
                    }
                }
                
                Spacer()
                
                // Test Notification Button
                Button(action: {
                    if let testMember = familyManager.familyMembers.first {
                        callMonitor.testGentleNudgeNotification(for: testMember)
                    }
                }) {
                    HStack {
                        Image(systemName: "bell.badge")
                        Text("Test Notification")
                            .fontWeight(.semibold)
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(
                        LinearGradient(
                            colors: [.orange, .red],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .cornerRadius(12)
                    .shadow(color: .orange.opacity(0.3), radius: 5, x: 0, y: 3)
                }
                .padding(.horizontal)
                .disabled(familyManager.familyMembers.isEmpty)
                
                // Add Member Button
                Button(action: {
                    showingAddMember = true
                }) {
                    HStack {
                        Image(systemName: "person.badge.plus")
                        Text("Add Family Member")
                            .fontWeight(.semibold)
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(
                        LinearGradient(
                            colors: [.purple, .pink],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .cornerRadius(12)
                    .shadow(color: .purple.opacity(0.3), radius: 5, x: 0, y: 3)
                }
                .padding(.horizontal)
                .padding(.bottom)
            }
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $showingAddMember) {
                AddFamilyMemberView(familyManager: familyManager)
            }
        }
    }
}

// MARK: - Family Member Card
struct FamilyMemberCard: View {
    let member: FamilyMember
    let onDelete: () -> Void
    
    var body: some View {
        HStack(spacing: 16) {
            // Avatar
            Circle()
                .fill(LinearGradient(colors: [.purple, .pink], startPoint: .topLeading, endPoint: .bottomTrailing))
                .frame(width: 50, height: 50)
                .overlay {
                    Text(String(member.name.prefix(1)).uppercased())
                        .font(.headline)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                }
            
            // Member Info
            VStack(alignment: .leading, spacing: 4) {
                Text(member.name)
                    .font(.headline)
                    .foregroundColor(.primary)
                
                Text(member.phoneNumber)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text("Safe Word: \(member.safeWordQuestion)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }
            
            Spacer()
            
            // Delete Button
            Button(action: onDelete) {
                Image(systemName: "trash")
                    .foregroundColor(.red)
                    .font(.caption)
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
    }
}

// MARK: - Add Family Member View
struct AddFamilyMemberView: View {
    let familyManager: FamilyCircleManager
    
    @State private var name = ""
    @State private var phoneNumber = ""
    @State private var safeWordQuestion = ""
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            Form {
                Section {
                    TextField("Name", text: $name)
                    TextField("Phone Number", text: $phoneNumber)
                        .keyboardType(.phonePad)
                    TextField("Safe Word Question", text: $safeWordQuestion)
                } header: {
                    Text("Family Member Details")
                } footer: {
                    Text("The safe word question will be shown as a reminder during calls from this person.")
                }
                
                Section {
                    Button("Save Family Member") {
                        let newMember = FamilyMember(
                            id: UUID().uuidString,
                            name: name,
                            phoneNumber: phoneNumber,
                            safeWordQuestion: safeWordQuestion
                        )
                        familyManager.addFamilyMember(newMember)
                        dismiss()
                    }
                    .disabled(name.isEmpty || phoneNumber.isEmpty || safeWordQuestion.isEmpty)
                }
            }
            .navigationTitle("Add Family Member")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    FamilyCircleView()
}