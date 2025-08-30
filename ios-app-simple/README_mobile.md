# Digital Guardian - iOS Anti-Scam Protection App

A comprehensive iOS app that protects users from scam calls and SMS messages using verified government contact data and family circle verification.

## Features

### 🛡️ Universal Verification System
- **Verified Contacts Database**: 410+ verified government and charity contacts
- **Real-time Verification**: Phone numbers, emails, and websites
- **Data Source**: Scraped from official government directories

### 👨‍👩‍👧‍👦 Family Circle Protection
- **Safe Word System**: Each family member has a unique verification question
- **CallKit Integration**: Real-time call monitoring and identification
- **Gentle Nudge Notifications**: 2-second delay after call connects
- **Visual Indicators**: 🛡️✅ for safe, 🚨❌ for scam contacts

### 📱 SMS Protection via Share Extension
- **Long-press Integration**: Share suspicious SMS messages for analysis
- **Threat Detection**: Checks against scam database and verified contacts
- **Risk Assessment**: Color-coded results (Red=Scam, Green=Safe, Yellow=Unknown)
- **Easy Testing**: Works with Reminders, Notes, Messages apps

## Technical Implementation

### Architecture
- **SwiftUI**: Modern iOS UI framework
- **CallKit**: Call monitoring and identification
- **UserNotifications**: Background notification system
- **Share Extension**: SMS analysis without app switching
- **App Groups**: Secure data sharing between app and extension

### Key Components
- `ContentView.swift`: Main app interface with verification tools
- `FamilyCircle.swift`: Family member management and safe word system
- `CallMonitor.swift`: CallKit integration for call state monitoring
- `NotificationHandler.swift`: Processes calls through verification pipeline
- `SMSAnalyzer.swift`: SMS threat detection engine
- `ShareViewController.swift`: Share Extension UI for SMS analysis

### Data Flow
1. **Incoming Call** → Family Circle → Verified Contacts → Scam Detection → Notification
2. **SMS Analysis** → Text Selection → Share Extension → Threat Database → Risk Assessment

## Setup

### Prerequisites
- Xcode 15+
- iOS 17+ simulator or device
- Apple Developer account (for device testing)

### Installation
1. Open `DigitalGuardianSimple.xcodeproj` in Xcode
2. Build and run on iOS simulator or device
3. Grant notification permissions when prompted

### Testing

#### Call Protection Testing
1. Use APNS files in `apns/` directory
2. Drag .apns files to iOS Simulator
3. Test with family member calls (Vin, Robyn, Adam, Jordan)

#### SMS Protection Testing
**Real Messages App Integration:**
1. Open **Messages** app on simulator
2. Create or receive SMS messages (works with real conversations)
3. Long-press on message bubble → **Share** → **Digital Guardian** 
4. Extension analyzes message against threat database
5. View comprehensive threat analysis with risk assessment

**Alternative Testing Methods:**
- **Reminders app**: Create reminder with test message, select text and share
- **Notes app**: Paste test message, select and share
- **Any app with text selection**: Select suspicious text and use share sheet

## Mock Data

### Family Members
- **Vin**: +61412345678 - "What was the name of our first pet?"
- **Robyn**: +61423456789 - "What street did we live on when we first met?"
- **Adam**: +61434567890 - "What was your favorite childhood movie?"
- **Jordan**: +61445678901 - "What was the name of your first school?"

### Test Messages
See `test_sms_messages.txt` for comprehensive scam and legitimate message examples.

## Screenshots

Latest screenshots available in `screenprints/` directory showing:
- Family Circle call identification with safe word prompts
- Visual notification indicators (green/red)
- SMS Share Extension in action
- Threat detection and analysis results

## Security Features

- **No API Keys in Code**: Secure external configuration
- **App Group Sandboxing**: Isolated data sharing
- **Privacy-First**: No personal data transmitted
- **Local Analysis**: All processing happens on-device

## GovHack 2025 Integration

Part of the broader anti-scam data pipeline project that:
1. Scrapes verified government contact information
2. Cross-references against scam databases
3. Provides real-time protection for mobile users
4. Helps citizens identify legitimate vs fraudulent contacts

Built using verified data from 400+ government services and threat intelligence sources.