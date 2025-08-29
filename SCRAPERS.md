# Scraper Reference Guide

This file documents which scrapers are proven to work and should be used in the multi-agent pipeline, and which ones are historical/failed attempts that should be avoided.

## ✅ **ACTIVE SCRAPERS** (Currently Used in Pipeline)

These scrapers are proven successful and are actively used in `backend/agents/agent_framework.py`:

### 1. **government_services_scraper.py** ✅
- **Success Rate**: 100% (109/109 records)
- **Data Source**: https://www.directory.gov.au/enquiry-lines
- **Method**: Unstructured web scraping with pagination
- **Output**: `data/raw/government_services.csv`
- **Quality**: Federal government phone numbers (1800, 1300, 13X numbers)
- **Status**: ✅ ACTIVE - Primary federal services scraper

### 2. **nsw_hospitals_agent.py** ✅  
- **Success Rate**: 100% (266/266 records)
- **Data Source**: NSW Health API via data.gov.au
- **Method**: Structured API data download
- **Output**: `data/raw/nsw_hospitals.csv`
- **Quality**: Complete NSW hospital dataset with phones, addresses, districts
- **Status**: ✅ ACTIVE - Best performing scraper

### 3. **scamwatch_threat_agent.py** ✅
- **Success Rate**: 100% (13/13 threat indicators)
- **Data Source**: https://www.scamwatch.gov.au/news-alerts
- **Method**: Threat intelligence extraction from news articles
- **Output**: `data/raw/scamwatch_threats.csv`
- **Quality**: Verified scam phone numbers and organization impersonation data
- **Status**: ✅ ACTIVE - Essential for threat detection

### 4. **acnc_data_agent.py** ✅
- **Success Rate**: 90% (5/5 charities in final dataset)
- **Data Source**: https://data.gov.au ACNC dataset + website scraping
- **Method**: Two-stage: CSV download + website contact extraction
- **Output**: `data/raw/acnc_charities_picton.csv`
- **Quality**: Verified charity contacts with phone/email from websites
- **Status**: ✅ ACTIVE - Proven charity data extraction

### 5. **nsw_correct_scraper.py** ✅
- **Success Rate**: 90% (9/10 agencies)
- **Data Source**: https://www.service.nsw.gov.au/nswgovdirectory/
- **Method**: Two-stage unstructured scraping (directory → agency pages)
- **Output**: `data/raw/nsw_correct_directory.csv`
- **Quality**: NSW government agencies with phone/email/website/addresses
- **Status**: ✅ ACTIVE - Uses correct URL pattern that works

---

## ❌ **HISTORICAL SCRAPERS** (Do NOT Use)

These scrapers had issues and should NOT be added to the pipeline:

### **nsw_focused_scraper.py** ❌
- **Issue**: Limited to 10 agencies, incomplete implementation
- **Status**: ❌ DEPRECATED - Use `nsw_correct_scraper.py` instead

### **nsw_gov_directory_scraper.py** ❌  
- **Issue**: Wrong URL patterns, low success rate
- **Status**: ❌ DEPRECATED - Use `nsw_correct_scraper.py` instead

### **acnc_charity_scraper.py** ❌
- **Issue**: Direct website scraping without API foundation
- **Status**: ❌ DEPRECATED - Use `acnc_data_agent.py` instead

### **acnc_enhanced_agent.py** ❌
- **Issue**: Over-engineered version with reliability issues
- **Status**: ❌ DEPRECATED - Use `acnc_data_agent.py` instead

### **website_contact_scraper.py** ❌
- **Issue**: Requires existing CSV input, not standalone
- **Status**: ❌ UTILITY ONLY - Not for pipeline, used by acnc_data_agent

---

## 🔧 **PIPELINE INTEGRATION CHECKLIST**

When adding a new scraper to the pipeline, ensure:

1. **✅ Update `agent_framework.py` collector_tasks list**:
   ```python
   collector_tasks = [
       ('scraper_name', 'backend/agents/scraper_file.py'),
   ]
   ```

2. **✅ Register agent in main() function**:
   ```python
   coordinator.register_agent(CollectorAgentProxy("scraper_name", "backend/agents/scraper_file.py"))
   ```

3. **✅ Update output path to save in `data/raw/`**:
   ```python
   def save_to_csv(self, data, filename='data/raw/output.csv'):
   ```

4. **✅ Update `data_standardizer.py` to process new data**:
   - Add filepath to relevant standardization method
   - Update Path references to use `data/raw/filename.csv`

5. **✅ Test end-to-end pipeline** with `python backend/run_pipeline.py`

---

## 📊 **SUCCESS METRICS**

For reference, proven scrapers achieve:
- **Success Rate**: 90-100% data extraction
- **Data Quality**: Grade A (95%+ quality score from Critic Agent)
- **Contact Coverage**: Phone numbers mandatory, email/website preferred
- **Format Compliance**: Australian phone number formats, valid emails
- **Source Reliability**: Official government/charity APIs preferred

---

## 🚫 **NEVER ADD THESE TO PIPELINE**

Files to avoid in agent_framework.py:
- `nsw_focused_scraper.py`
- `nsw_gov_directory_scraper.py` 
- `acnc_charity_scraper.py`
- `acnc_enhanced_agent.py`
- Any scraper with <90% success rate
- Any scraper without proper `data/raw/` output paths

---

## 📝 **CURRENT PIPELINE STATUS**

**Pipeline Command**: `python backend/run_pipeline.py`

**Active Agents**: 5 collectors + 2 processors
- ✅ government_services_scraper (109 records)
- ✅ nsw_hospitals_agent (266 records)  
- ✅ scamwatch_threat_agent (13 records)
- ✅ acnc_data_agent (5 records)
- ✅ nsw_correct_scraper (9 records)

**Results**: 402 safe contacts, 13 threat indicators, Grade A quality (95%)

**Last Updated**: 2025-08-30 - Enhanced pipeline with all proven scrapers