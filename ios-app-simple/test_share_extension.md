# Quick Test Instructions for Share Extension

## Without iMessage Setup:

1. **Run Main App First**
   - Select "DigitalGuardianSimple" when prompted
   - Click "Run"
   - Let it install completely

2. **Test from Notes App**
   - Open Notes app on simulator
   - Create a new note
   - Paste one of these test messages:

```
ATO: You have a tax refund of $850 pending. Click here to claim immediately: bit.ly/taxrefund2025
Call 1800 595 160 for assistance.
```

3. **Share to Extension**
   - Select the text
   - Tap Share button
   - Choose "Digital Guardian"
   - Extension will analyze and show if it's a scam

## Expected Results:

- **SCAM Messages**: Red warning with threat details
- **LEGITIMATE Messages**: Green safe indicator
- **UNKNOWN**: Yellow caution for unverified contacts

The extension checks against 400+ verified government contacts in the CSV database.