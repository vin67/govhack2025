# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a GovHack 2025 project building a multi-agent data pipeline to collect and verify government service contact information. The system extracts legitimate government and charity phone numbers/websites, then cross-references against scam databases to help people identify legitimate vs fraudulent contacts.

## Architecture

Multi-agent pipeline using Google's Agent Development Kit (ADK) and Agent2Agent (A2A) protocol:

1. **Collector Agents**: Gather data from various sources
   - Structured Data Agent (data.gov.au APIs/CSV)
   - Unstructured Data Agent (web scraping government sites)
   - Scamwatch Agent (threat intelligence)

2. **Critic Agent**: Data validation and quality assurance
3. **Sorter Agent**: Categorizes into output CSV files

## Technology Stack

- **Language**: Python 3
- **Framework**: Google Agent Development Kit (ADK)
- **Communication**: Agent2Agent (A2A) Protocol
- **Web Scraping**: requests, BeautifulSoup4
- **Data Processing**: CSV, pandas (planned)
- **AI Integration**: LLMLite (planned)

## Development Commands

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test government services scraper
python test_scraper.py

# Run full government services extraction
python gov_services_scraper.py

# Run individual agents (planned)
python agents/unstructured_agent.py
```

## Current Implementation

### Completed
- **Government Services Scraper**: Extracts service names and phone numbers from directory.gov.au
- **Data Structure**: Cleanly formatted CSV output with service details
- **Rate Limiting**: Respectful scraping with delays

### File Structure
```
gov_services_scraper.py    # Main unstructured data agent
test_scraper.py           # Test script for single page
requirements.txt          # Python dependencies
test_services.csv         # Sample output data
```

### Next Steps
- Implement Google ADK framework
- Create A2A protocol communication
- Add structured data agents for APIs
- Build scamwatch threat intelligence agent
- Implement critic agent for data validation