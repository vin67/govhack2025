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
│   ├── DigitalGuardianSimpleApp.swift    # Main app entry point
│   ├── ContentView.swift                 # Hello World UI
│   └── [Additional Swift files]
└── README_mobile.md                      # This file
```

## Core Features (Planned)

### Phase 1: Hello World + Basic Structure
- ✅ Basic SwiftUI interface
- ✅ Modern iOS 17+ design  
- ✅ Claude-assisted development setup
- 🔄 Git integration with main repository

### Phase 2: SMS Protection
- 📱 **Share Sheet Integration**: Long-press SMS → Share → Digital Guardian
- 🔍 **Text Analysis**: Parse phone numbers, URLs, suspicious patterns
- ⚠️ **Threat Detection**: Cross-reference with backend CSV data
- 🎯 **Senior Mode**: Large text, simplified alerts, accessible design

### Phase 3: Call Protection  
- 📞 **Smart Caller ID**: Display scam warnings on incoming calls
- 🛡️ **CallKit Integration**: Native iOS call screening
- 🔢 **Number Checker**: Manual lookup tool for suspicious numbers
- 🌐 **Link Checker**: Website/URL verification tool

### Phase 4: Family Protection
- 👥 **Family Circle**: Secret questions for voice clone detection
- 🔒 **Secure Callback**: Bypass caller ID spoofing with verified contacts
- 🆘 **Emergency Support**: Quick access to community navigators

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

### Current Phase: Hello World Setup
1. **Create Xcode Project**: Basic SwiftUI app structure
2. **Test Claude Integration**: Verify AI assistance works
3. **Git Integration**: Connect with main GovHack repository
4. **Basic UI**: Foundation for future features

### Next Phase: Core Functionality
1. **Data Models**: Contact, Threat, Verification structures
2. **CSV Loader**: Import backend pipeline data
3. **Share Extension**: Basic SMS text analysis
4. **Simple UI**: Number/link checker tool

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