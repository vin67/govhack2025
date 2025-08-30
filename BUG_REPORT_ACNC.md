# Bug Report: ACNC Charity Contact Details Extraction

## Issue Summary
**Status**: Open  
**Priority**: Medium  
**Component**: ACNC Data Agent  
**Reporter**: GovHack 2025 Team  
**Date**: 2025-08-30  

## Problem Description
Unable to extract phone numbers, email addresses, and website URLs from individual ACNC (Australian Charities and Not-for-profits Commission) charity profile pages due to JavaScript-rendered content and potential bot protection mechanisms.

## Current Behavior
- ✅ Successfully extract organizational data (charity names, ABNs, addresses, purposes) from ACNC CSV bulk data
- ✅ Can identify charity profile URLs in format: `https://www.acnc.gov.au/charity/charities/[ID]/profile`
- ❌ Contact details (phone/email/website) are not accessible via standard HTTP requests
- ❌ ACNC search results table is loaded dynamically and not present in initial HTML response

## Expected Behavior
- Should be able to extract contact information from charity profiles for:
  - **Caller identification**: Verify incoming calls from legitimate charities
  - **Callback functionality**: Enable users to contact verified charities directly
  - **Anti-scam verification**: Cross-reference caller details with official records

## Technical Analysis

### Root Cause
ACNC website implements several protection mechanisms:

1. **JavaScript-Rendered Content**: 
   - Search results table with `data-v-5f6e0f24` attributes loaded via Vue.js
   - Contact details rendered client-side, not in initial HTML response

2. **Bot Protection**: 
   - Likely intentional to prevent automated harvesting of charity contact details
   - Protects charities from unwanted solicitation and spam

3. **Dynamic Content Loading**:
   - Search URL `https://www.acnc.gov.au/charity/charities?location=picton` returns empty results in HTML
   - Actual data populated after JavaScript execution

### Evidence
```bash
# Search page returns empty results
$ curl "https://www.acnc.gov.au/charity/charities?location=picton"
# Returns: 0 tables, 0 charity links, 0 'picton' matches

# Profile pages accessible but contact details require JavaScript
$ curl "https://www.acnc.gov.au/charity/charities/[ID]/profile" 
# Returns: Basic HTML structure but missing contact information
```

## Impact Assessment

### Current Impact
- **Low**: Organizational verification still works (names, ABNs, addresses available)
- **Medium**: Missing contact details limits app functionality for legitimate callbacks
- **Medium**: Reduces completeness of anti-scam database

### User Experience Impact
- Users cannot easily contact verified charities through the app
- Caller ID feature limited to organization names only (no phone number verification)
- Potential false negatives: legitimate charity calls may appear unverified

## Potential Solutions

### Option 1: Browser Automation (Selenium)
```python
# Pros: Can access JavaScript-rendered content
# Cons: Resource intensive, slower, may still be blocked
from selenium import webdriver
driver = webdriver.Chrome()
# Implementation would extract contact details after page load
```

### Option 2: Alternative Data Sources
- **ABN Lookup Service**: `https://abr.business.gov.au/` may provide contact details
- **Data.gov.au APIs**: Explore additional government datasets
- **Charity annual reports**: May contain contact information in structured formats

### Option 3: ACNC API Integration
- **Official API**: Contact ACNC for potential API access for legitimate anti-scam purposes
- **Research partnership**: Formal collaboration for public safety initiatives

### Option 4: Hybrid Approach
- Use existing organizational data for verification
- Allow users to manually add verified contact details
- Crowd-sourced verification with moderation

## Workaround (Current Implementation)
```python
# We currently provide organizational verification without contact details
charity_record = {
    'charity_name': 'His House Incorporated',
    'abn': '20160089146', 
    'address': '54 Bridge St, Picton, NSW, 2571',
    'phone': '',  # Not available due to JavaScript protection
    'email': '',  # Not available due to JavaScript protection
    'website': '', # Not available due to JavaScript protection
    'verification_status': 'ACNC_VERIFIED',
    'risk_level': 'safe'
}
```

## Security Considerations

### Why ACNC Blocks Automated Access
1. **Privacy Protection**: Prevents mass harvesting of charity contact details
2. **Spam Prevention**: Protects charities from automated solicitation
3. **Data Integrity**: Ensures contact information is accessed by humans only
4. **Compliance**: May be required by privacy legislation

### Anti-Scam vs. Privacy Balance
- **Legitimate Use**: Our anti-scam purpose is beneficial to charities
- **Potential Abuse**: Same techniques could be used maliciously
- **Solution**: Formal partnership or API access would resolve both concerns

## Recommendations

### Immediate Actions
1. **Document limitation** in user-facing materials
2. **Implement caller ID** based on organization names only
3. **Add manual contact entry** feature for verified users

### Future Enhancements
1. **Contact ACNC** for official API access discussions
2. **Explore ABN Lookup Service** integration
3. **Research partnership opportunities** with government anti-scam initiatives
4. **Implement browser automation** if performance requirements allow

## Notes for Hackathon Context
- This limitation is **expected and reasonable** for a hackathon prototype
- Demonstrates understanding of **real-world data protection mechanisms**
- Shows **ethical approach** to data collection and privacy considerations
- **Alternative solutions identified** for production implementation

## Related Issues
- Caller ID spoofing remains a challenge regardless of contact database completeness  
- Phone number verification limited by telco infrastructure, not data availability
- Geographic validation still possible through address verification

---

**Status**: Documented for future resolution  
**Next Review**: Post-hackathon for potential ACNC partnership discussion