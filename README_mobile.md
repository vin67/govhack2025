# Digital Guardian Mobile - iOS App

A GovHack 2025 anti-scam protection iOS app, built with Xcode 26 Beta 7 and Claude integration.

## Project Overview

Digital Guardian Mobile is an iOS app designed to protect vulnerable Australians from phone and SMS scams. It provides real-time threat detection, SMS analysis via Share Sheet, and connects users with community support when needed.

## Development Environment

### Prerequisites
- Xcode 26 Beta 7 
- macOS 26 Tahoe (beta)
- Claude Sonnet 4 account configured in Xcode
- iOS 17.0+ target devices

### Claude Integration Features
- **Claude Sonnet 4** for architectural decisions and complex iOS patterns
- **Native code completion** with AI assistance
- **SwiftUI layout help** optimized for accessibility
- **iOS permissions guidance** (CallKit, MessageFilter, Share Extensions)

## Project Structure

```
ios-app-simple/
├── DigitalGuardianSimple/
│   ├── DigitalGuardianSimpleApp.swift    # Main app entry point with CallKit integration
│   ├── ContentView.swift                 # TabView UI with Protection & Family Circle tabs
│   ├── VerificationView.swift            # Universal contact verification (phone/email/website)
│   ├── DataManager.swift                 # CSV data processing for 410+ verified contacts
│   ├── FamilyCircle.swift                # Family member data models and management
│   ├── FamilyCircleView.swift            # Family Circle setup and management UI
│   ├── CallMonitor.swift                 # CallKit call observer for real-time monitoring
│   ├── NotificationHandler.swift         # Gentle nudge notification system
│   ├── mock_family_circle.json          # Test data (Vin, Robyn, Adam, Jordan)
│   └── sorted_contacts_master.csv        # 410+ verified Australian contacts
└── README_mobile.md                      # This file
```

## Core Features (Implemented)

### ✅ Phase 1: Universal Verification System
- ✅ **Phone Number Verification**: Check against 410+ verified Australian government services
- ✅ **Email Verification**: Verify official government department email addresses  
- ✅ **Website Verification**: Confirm legitimate government and charity websites
- ✅ **Real-time Results**: Instant feedback with confidence scores and organization details
- ✅ **CSV Data Integration**: Processes sorted_contacts_master.csv with verified contacts

### ✅ Phase 2: Family Circle Protection (NEW)
- ✅ **Family Member Management**: Add/remove family contacts with safe word questions
- ✅ **Mock Testing Data**: Pre-configured test contacts (Vin, Robyn, Adam, Jordan)
- ✅ **CallKit Integration**: Real-time call monitoring and state detection
- ✅ **Gentle Nudge Notifications**: Discrete reminders during family member calls
- ✅ **Safe Word System**: Security questions to verify family member authenticity
- ✅ **Secure Callback Options**: Quick access to verified contact numbers

### ✅ Phase 3: Advanced Protection Framework
- ✅ **TabView Navigation**: Dual-tab interface (Protection + Family Circle)
- ✅ **Background Monitoring**: Continuous call monitoring with CallKit
- ✅ **Notification Actions**: Interactive notifications with callback options
- ✅ **Privacy-First Design**: All processing happens on-device
- ✅ **Debug/Release Modes**: Smart data loading for development vs production

### 🔄 Phase 4: Extensions & SMS Protection (In Progress)
- 📱 **MessageFilter Extension**: SMS filtering against verified contacts
- 🛡️ **Call Directory Extension**: Enhanced caller ID with government contact labels
- 📞 **Smart Caller ID**: Display verified organization names for incoming calls
- 🔍 **Scam Pattern Detection**: Intelligent analysis of suspicious message content

## Technical Architecture

### Data Integration
- 📊 **Backend CSV Integration**: Uses existing GovHack pipeline data
- 🏥 **Government Contacts**: Hospital, agency, service numbers
- 🚨 **Threat Database**: Known scam numbers and patterns
- ✅ **Verification System**: Safe contact whitelist

### iOS-Specific Features
- 🔗 **Share Extensions**: Receive text from Messages app
- 📞 **CallKit Extensions**: Call identification and blocking
- 🎛️ **MessageFilter**: SMS filtering (iOS 14+)
- ♿ **Accessibility**: VoiceOver, Dynamic Type, high contrast

## Development Phases

### ✅ Completed: Full Protection Suite
1. **Universal Verification**: Phone, email, website checking against 410+ verified contacts
2. **Family Circle System**: Safe word protection with CallKit monitoring
3. **Real-time Notifications**: Gentle nudge system for family member calls
4. **Modern SwiftUI Interface**: TabView with Protection and Family Circle tabs

### 🔄 Current Phase: iOS Extensions
1. **MessageFilter Extension**: SMS filtering using IdentityLookup framework
2. **Call Directory Extension**: Enhanced caller ID with CallKit integration
3. **App Group Data Sharing**: Secure contact data sharing between extensions
4. **Advanced Scam Detection**: Pattern recognition and threat intelligence

### 🎯 Next Phase: Testing & Polish
1. **Physical Device Testing**: Real iPhone testing with actual phone calls
2. **Notification Permission Flow**: Streamlined user onboarding
3. **Performance Optimization**: Background processing and battery efficiency
4. **Accessibility Enhancement**: VoiceOver and Dynamic Type support

## Getting Started

### Setup Instructions

1. **Open Xcode 26 Beta 7**

2. **Create New Project:**
   ```
   Product Name: DigitalGuardianSimple
   Bundle ID: com.govhack.digitalguardian.simple
   Language: Swift
   Interface: SwiftUI
   iOS Target: 17.0+
   ```

3. **Configure Claude:**
   - Open Xcode Intelligence settings
   - Add Claude Sonnet 4 account
   - Test AI code completion

4. **Import Source Files:**
   - Copy Swift files from `ios-app-simple/DigitalGuardianSimple/`
   - Build and run in simulator

### Testing with Claude

Try these prompts in Xcode with Claude:
- "Create an accessible button for senior users"
- "Help me parse phone numbers from text"  
- "Design a SwiftUI Share Sheet extension"
- "Implement CallKit caller ID display"

## Integration with Backend

This iOS app integrates with the existing GovHack 2025 multi-agent pipeline:

### Data Sources
- `data/verified/government_contacts.csv` - Safe government numbers
- `data/verified/hospital_contacts.csv` - Verified hospital contacts  
- `data/threats/threat_contacts.csv` - Known scam numbers
- `data/sorted_contacts_master.csv` - Complete verified dataset

### Pipeline Integration
- **Real-time Updates**: Sync with latest CSV exports
- **Quality Scores**: Use confidence ratings from critic agent
- **Risk Assessment**: Leverage sorter agent categorizations
- **Community Support**: Connect to navigator platform

## Accessibility & User Experience

### Design Principles
- **Senior-Friendly**: Large text, simple navigation, clear alerts
- **Accessibility First**: VoiceOver, Dynamic Type, high contrast support
- **Crisis-Ready**: Clear, unambiguous warnings and help options
- **Privacy-Focused**: On-device processing, minimal data collection

### User Personas
- **Primary**: Older Australians (75+) with low digital ability
- **Secondary**: CALD communities, people with disabilities
- **Support**: Family members and community navigators

## Security & Privacy

- 🔒 **On-Device Processing**: SMS analysis happens locally
- 🚫 **No Data Collection**: App doesn't store or transmit personal messages
- ✅ **Verified Sources**: Only uses official government and charity data
- 🛡️ **Apple Privacy**: Follows iOS security best practices

## Future Enhancements

- 🤖 **AI Voice Detection**: Identify synthetic voice calls
- 🌐 **Real-time Updates**: Live threat intelligence feeds
- 📱 **Cross-Platform**: Android version using React Native
- 🏢 **Enterprise**: Version for aged care facilities and community centers

## Contributing

This is a GovHack 2025 project. Development is focused on creating a working prototype that demonstrates the anti-scam protection concept using Australian government data.

### Development Workflow
1. Use Claude assistance in Xcode for complex iOS features
2. Test regularly on iOS simulator and devices
3. Commit to Git with descriptive messages
4. Focus on accessibility and senior-friendly design

---

**GovHack 2025 Team Project**  
Building safer digital experiences for all Australians 🇦🇺🛡️