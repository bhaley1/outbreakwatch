#!/usr/bin/env python3
"""
OutbreakWatch Data Updater - Simplified Version
Scrapes WHO DON and CDC alerts to update outbreak data daily
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os

def scrape_who_don():
    """Scrape WHO Disease Outbreak News for recent alerts"""
    alerts = []
    try:
        url = "https://www.who.int/emergencies/disease-outbreak-news"
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; OutbreakWatch/1.0)'}
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # For now, just log that we successfully connected
            print("✓ Successfully connected to WHO DON")
            print(f"✓ Response status: {response.status_code}")
            
            # Parse the page for outbreak information
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text().lower()
            
            # Check for key outbreak terms
            outbreak_terms = ['ebola', 'outbreak', 'cases', 'deaths', 'pheic']
            found_terms = [term for term in outbreak_terms if term in page_text]
            
            if found_terms:
                alerts.append({
                    "source": "WHO DON",
                    "terms_found": found_terms,
                    "url": url,
                    "timestamp": datetime.now().isoformat()
                })
                print(f"✓ Found outbreak-related terms: {', '.join(found_terms)}")
            else:
                print("ℹ️ No specific outbreak terms detected")
                
    except Exception as e:
        print(f"❌ WHO DON scraping failed: {e}")
    
    return alerts

def scrape_cdc_outbreaks():
    """Scrape CDC Current Outbreaks"""
    alerts = []
    try:
        url = "https://www.cdc.gov/outbreaks/index.html"
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; OutbreakWatch/1.0)'}
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("✓ Successfully connected to CDC Outbreaks")
            print(f"✓ Response status: {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text().lower()
            
            # Check for outbreak terms
            outbreak_terms = ['salmonella', 'e. coli', 'listeria', 'outbreak', 'cases']
            found_terms = [term for term in outbreak_terms if term in page_text]
            
            if found_terms:
                alerts.append({
                    "source": "CDC Outbreaks",
                    "terms_found": found_terms,
                    "url": url,
                    "timestamp": datetime.now().isoformat()
                })
                print(f"✓ Found outbreak-related terms: {', '.join(found_terms)}")
            else:
                print("ℹ️ No specific outbreak terms detected")
                
    except Exception as e:
        print(f"❌ CDC scraping failed: {e}")
    
    return alerts

def save_outbreak_data(who_alerts, cdc_alerts):
    """Save scraped data to JSON file"""
    data = {
        "last_updated": datetime.now().isoformat(),
        "who_alerts": who_alerts,
        "cdc_alerts": cdc_alerts,
        "total_alerts": len(who_alerts) + len(cdc_alerts)
    }
    
    try:
        with open('outbreak_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("✓ Outbreak data saved to outbreak_data.json")
        return True
    except Exception as e:
        print(f"❌ Failed to save data: {e}")
        return False

def main():
    """Main execution function"""
    print("🌍 Starting OutbreakWatch daily update...")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Scrape data sources
    who_alerts = scrape_who_don()
    cdc_alerts = scrape_cdc_outbreaks()
    
    # Save the data
    success = save_outbreak_data(who_alerts, cdc_alerts)
    
    if success:
        print(f"✅ Daily update completed successfully")
        print(f"📊 WHO alerts: {len(who_alerts)}")
        print(f"📊 CDC alerts: {len(cdc_alerts)}")
    else:
        print("❌ Daily update failed")
        exit(1)

if __name__ == "__main__":
    main()
