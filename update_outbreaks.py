#!/usr/bin/env python3
"""
OutbreakWatch Data Updater
Scrapes WHO DON and CDC alerts to update outbreak data daily
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os

class OutbreakScraper:
    def __init__(self):
        self.data = {
            "last_updated": datetime.now().isoformat(),
            "critical_threats": [],
            "outbreak_monitoring": []
        }
    
    def scrape_who_don(self):
        """Scrape WHO Disease Outbreak News"""
        try:
            url = "https://www.who.int/emergencies/disease-outbreak-news"
            headers = {'User-Agent': 'Mozilla/5.0 (OutbreakWatch Surveillance Bot)'}
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for recent outbreak news items
                news_items = soup.find_all('div', class_='card-item')[:5]  # Get top 5
                
                for item in news_items:
                    title_elem = item.find('h3') or item.find('h2') or item.find('a')
                    if title_elem:
                        title = title_elem.get_text().strip()
                        link_elem = item.find('a')
                        link = link_elem.get('href') if link_elem else ""
                        
                        # Classify by keywords
                        if any(keyword in title.lower() for keyword in ['ebola', 'marburg', 'pheic', 'emergency']):
                            self.data["critical_threats"].append({
                                "type": "hcid",
                                "title": title,
                                "source": "WHO DON",
                                "link": f"https://www.who.int{link}" if link.startswith('/') else link,
                                "date": datetime.now().strftime("%Y-%m-%d")
                            })
                        elif any(keyword in title.lower() for keyword in ['outbreak', 'cases', 'surveillance']):
                            self.data["outbreak_monitoring"].append({
                                "type": "general",
                                "title": title,
                                "source": "WHO DON", 
                                "link": f"https://www.who.int{link}" if link.startswith('/') else link,
                                "date": datetime.now().strftime("%Y-%m-%d")
                            })
                            
            print("✓ WHO DON scraping completed")
            
        except Exception as e:
            print(f"❌ WHO DON scraping failed: {e}")
    
    def scrape_cdc_outbreaks(self):
        """Scrape CDC Current Outbreaks"""
        try:
            url = "https://www.cdc.gov/outbreaks/index.html"
            headers = {'User-Agent': 'Mozilla/5.0 (OutbreakWatch Surveillance Bot)'}
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for outbreak listings
                outbreak_sections = soup.find_all(['div', 'section'], class_=re.compile(r'outbreak|alert|notice'))
                
                for section in outbreak_sections[:5]:  # Limit to prevent overload
                    links = section.find_all('a')
                    for link in links:
                        title = link.get_text().strip()
                        href = link.get('href', '')
                        
                        if len(title) > 20 and any(keyword in title.lower() for keyword in 
                            ['salmonella', 'e. coli', 'listeria', 'outbreak', 'measles', 'hantavirus']):
                            
                            self.data["outbreak_monitoring"].append({
                                "type": "foodborne" if any(fb in title.lower() for fb in ['salmonella', 'e. coli', 'listeria']) else "vpd",
                                "title": title,
                                "source": "CDC",
                                "link": f"https://www.cdc.gov{href}" if href.startswith('/') else href,
                                "date": datetime.now().strftime("%Y-%m-%d")
                            })
                            
            print("✓ CDC Outbreaks scraping completed")
            
        except Exception as e:
            print(f"❌ CDC scraping failed: {e}")
    
    def scrape_cdc_measles(self):
        """Scrape CDC Measles data specifically"""
        try:
            url = "https://www.cdc.gov/measles/data-research/index.html"
            headers = {'User-Agent': 'Mozilla/5.0 (OutbreakWatch Surveillance Bot)'}
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for case numbers
                text = soup.get_text()
                measles_match = re.search(r'(\d{1,4})\s+confirmed.*measles.*cases.*reported.*(\d{4})', text, re.IGNORECASE)
                
                if measles_match:
                    cases = measles_match.group(1)
                    year = measles_match.group(2)
                    
                    self.data["outbreak_monitoring"].append({
                        "type": "vpd",
                        "title": f"Measles Cases in US {year}: {cases} confirmed cases",
                        "source": "CDC Measles Surveillance",
                        "link": url,
                        "cases": int(cases),
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                    
            print("✓ CDC Measles scraping completed")
            
        except Exception as e:
            print(f"❌ CDC Measles scraping failed: {e}")
    
    def update_html(self):
        """Update the HTML file with new data"""
        try:
            # Read the current HTML template
            with open('index_template.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Replace placeholders with actual data
            # This would need specific placeholder markers in your HTML
            
            # For now, just save the data as JSON for manual integration
            with open('outbreak_data.json', 'w') as f:
                json.dump(self.data, f, indent=2)
                
            print("✓ Data saved to outbreak_data.json")
            
        except Exception as e:
            print(f"❌ HTML update failed: {e}")
    
    def run_daily_update(self):
        """Run the complete daily update process"""
        print("🌍 Starting OutbreakWatch daily update...")
        
        self.scrape_who_don()
        self.scrape_cdc_outbreaks()
        self.scrape_cdc_measles()
        self.update_html()
        
        print(f"✅ Daily update completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Found {len(self.data['critical_threats'])} critical threats")
        print(f"📊 Found {len(self.data['outbreak_monitoring'])} outbreak alerts")

if __name__ == "__main__":
    scraper = OutbreakScraper()
    scraper.run_daily_update()
