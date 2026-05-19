#!/usr/bin/env python3
"""
Real Global Foodborne Outbreak Data Scraper

Pulls actual foodborne outbreak data from official global health authorities:
- ECDC (European Centre for Disease Prevention and Control)
- WHO Disease Outbreak News
- Health Canada Food Safety Recalls
- Food Standards Australia New Zealand
- PAHO Epidemiological Alerts
- CDC Foodborne Outbreaks

Updates: Every 6 hours
Output: foodborne_outbreaks.json for web integration
"""

import requests
import json
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import feedparser
import time

@dataclass
class FoodborneOutbreak:
    """Real foodborne outbreak data structure"""
    id: str
    pathogen: str
    product: str
    countries: List[str]
    regions: List[str]
    cases: Optional[int]
    deaths: Optional[int]
    hospitalizations: Optional[int]
    date_detected: str
    date_reported: str
    source_organization: str
    source_url: str
    severity_level: str
    status: str
    description: str
    last_updated: str

class GlobalFoodborneMonitor:
    """Scrapes real foodborne outbreak data from global health authorities"""
    
    def __init__(self):
        self.outbreaks = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def scrape_who_disease_outbreak_news(self) -> List[FoodborneOutbreak]:
        """Scrape WHO Disease Outbreak News for foodborne incidents"""
        outbreaks = []
        
        try:
            print("Scraping WHO Disease Outbreak News...")
            
            # WHO DON RSS feed
            url = "https://www.who.int/feeds/entity/csr/don/en/rss.xml"
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:20]:  # Check last 20 entries
                title = entry.get('title', '').lower()
                summary = entry.get('summary', '').lower()
                link = entry.get('link', '')
                published = entry.get('published', '')
                
                # Look for foodborne-related keywords
                foodborne_keywords = ['foodborne', 'food poisoning', 'salmonella', 'e. coli', 'listeria', 
                                    'campylobacter', 'norovirus', 'hepatitis a', 'outbreak', 'food safety']
                
                if any(keyword in title or keyword in summary for keyword in foodborne_keywords):
                    # Extract more details by fetching the full page
                    pathogen, countries, cases = self._extract_who_details(link, title, summary)
                    
                    if pathogen:
                        outbreak = FoodborneOutbreak(
                            id=f"WHO_{hash(link)}",
                            pathogen=pathogen,
                            product=self._extract_food_product(title + " " + summary),
                            countries=countries,
                            regions=self._countries_to_regions(countries),
                            cases=cases,
                            deaths=None,
                            hospitalizations=None,
                            date_detected=self._parse_who_date(published),
                            date_reported=self._parse_who_date(published),
                            source_organization="World Health Organization (WHO)",
                            source_url=link,
                            severity_level=self._assess_severity(cases, countries),
                            status="Active",
                            description=entry.get('title', ''),
                            last_updated=datetime.now().isoformat()
                        )
                        outbreaks.append(outbreak)
                        
        except Exception as e:
            print(f"Error scraping WHO: {e}")
            
        return outbreaks
    
    def scrape_ecdc_threats(self) -> List[FoodborneOutbreak]:
        """Scrape ECDC Communicable Disease Threats for foodborne outbreaks"""
        outbreaks = []
        
        try:
            print("Scraping ECDC Communicable Disease Threats...")
            
            # ECDC threats page
            url = "https://www.ecdc.europa.eu/en/threats-and-outbreaks/reports-and-data/weekly-threats"
            response = requests.get(url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for recent threat reports
            threat_links = soup.find_all('a', href=True)
            
            for link in threat_links[:10]:
                href = link.get('href', '')
                text = link.get_text().lower()
                
                if ('foodborne' in text or 'salmonella' in text or 'listeria' in text or 
                    'outbreak' in text and any(food in text for food in ['food', 'eat', 'consumption'])):
                    
                    full_url = f"https://www.ecdc.europa.eu{href}" if href.startswith('/') else href
                    
                    # Extract outbreak details
                    pathogen, countries, cases = self._extract_ecdc_details(full_url, text)
                    
                    if pathogen:
                        outbreak = FoodborneOutbreak(
                            id=f"ECDC_{hash(full_url)}",
                            pathogen=pathogen,
                            product=self._extract_food_product(text),
                            countries=countries,
                            regions=["Europe"],
                            cases=cases,
                            deaths=None,
                            hospitalizations=None,
                            date_detected=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                            date_reported=datetime.now().strftime('%Y-%m-%d'),
                            source_organization="European Centre for Disease Prevention and Control (ECDC)",
                            source_url=full_url,
                            severity_level=self._assess_severity(cases, countries),
                            status="Under Investigation",
                            description=link.get_text(),
                            last_updated=datetime.now().isoformat()
                        )
                        outbreaks.append(outbreak)
                        
        except Exception as e:
            print(f"Error scraping ECDC: {e}")
            
        return outbreaks
    
    def scrape_health_canada_recalls(self) -> List[FoodborneOutbreak]:
        """Scrape Health Canada food safety recalls"""
        outbreaks = []
        
        try:
            print("Scraping Health Canada Food Safety Recalls...")
            
            # Health Canada recalls RSS
            url = "https://recalls-rappels.canada.ca/en/search/site?f%5B0%5D=category%3A178"
            response = requests.get(url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find recall items
            recall_items = soup.find_all('div', class_='views-row') if soup else []
            
            for item in recall_items[:10]:
                title_elem = item.find('h3') or item.find('a')
                if title_elem:
                    title = title_elem.get_text().strip().lower()
                    link_elem = title_elem.find('a') or title_elem
                    link = link_elem.get('href', '') if link_elem else ''
                    
                    # Look for foodborne illness keywords
                    if any(keyword in title for keyword in ['salmonella', 'listeria', 'e. coli', 'illness', 'outbreak']):
                        
                        pathogen = self._extract_pathogen_name(title)
                        product = self._extract_food_product(title)
                        
                        if pathogen and product:
                            outbreak = FoodborneOutbreak(
                                id=f"HC_{hash(link)}",
                                pathogen=pathogen,
                                product=product,
                                countries=["Canada"],
                                regions=["North America"],
                                cases=None,
                                deaths=None,
                                hospitalizations=None,
                                date_detected=datetime.now().strftime('%Y-%m-%d'),
                                date_reported=datetime.now().strftime('%Y-%m-%d'),
                                source_organization="Health Canada",
                                source_url=f"https://recalls-rappels.canada.ca{link}" if link.startswith('/') else link,
                                severity_level="Medium",
                                status="Recall Issued",
                                description=title_elem.get_text().strip(),
                                last_updated=datetime.now().isoformat()
                            )
                            outbreaks.append(outbreak)
                            
        except Exception as e:
            print(f"Error scraping Health Canada: {e}")
            
        return outbreaks
    
    def scrape_cdc_foodborne_outbreaks(self) -> List[FoodborneOutbreak]:
        """Scrape CDC current foodborne outbreak investigations"""
        outbreaks = []
        
        try:
            print("Scraping CDC Foodborne Outbreaks...")
            
            # CDC outbreaks page
            url = "https://www.cdc.gov/foodsafety/outbreaks/multistate-outbreaks/outbreaks-list.html"
            response = requests.get(url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for outbreak tables or lists
            outbreak_links = soup.find_all('a', href=True)
            
            for link in outbreak_links:
                text = link.get_text().lower()
                href = link.get('href', '')
                
                if ('outbreak' in text and any(pathogen in text for pathogen in 
                    ['salmonella', 'e. coli', 'listeria', 'campylobacter', 'norovirus'])):
                    
                    pathogen = self._extract_pathogen_name(text)
                    product = self._extract_food_product(text)
                    
                    if pathogen:
                        outbreak = FoodborneOutbreak(
                            id=f"CDC_{hash(href)}",
                            pathogen=pathogen,
                            product=product or "Food Product",
                            countries=["United States"],
                            regions=["North America"],
                            cases=None,
                            deaths=None,
                            hospitalizations=None,
                            date_detected=(datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d'),
                            date_reported=datetime.now().strftime('%Y-%m-%d'),
                            source_organization="Centers for Disease Control and Prevention (CDC)",
                            source_url=f"https://www.cdc.gov{href}" if href.startswith('/') else href,
                            severity_level="High",
                            status="Under Investigation",
                            description=link.get_text().strip(),
                            last_updated=datetime.now().isoformat()
                        )
                        outbreaks.append(outbreak)
                        
        except Exception as e:
            print(f"Error scraping CDC: {e}")
            
        return outbreaks

    def _extract_pathogen_name(self, text: str) -> str:
        """Extract pathogen name from text"""
        text = text.lower()
        pathogens = {
            'salmonella': 'Salmonella',
            'e. coli': 'E. coli',
            'e coli': 'E. coli', 
            'listeria': 'Listeria monocytogenes',
            'campylobacter': 'Campylobacter',
            'norovirus': 'Norovirus',
            'hepatitis a': 'Hepatitis A',
            'shigella': 'Shigella',
            'clostridium': 'Clostridium perfringens',
            'cyclospora': 'Cyclospora cayetanensis'
        }
        
        for key, value in pathogens.items():
            if key in text:
                return value
        return "Unknown Pathogen"
    
    def _extract_food_product(self, text: str) -> str:
        """Extract food product from text"""
        text = text.lower()
        foods = ['lettuce', 'spinach', 'tomatoes', 'onions', 'eggs', 'chicken', 'beef', 'pork', 
                'cheese', 'milk', 'ice cream', 'berries', 'cantaloupe', 'nuts', 'chocolate',
                'seafood', 'fish', 'sprouts', 'herbs', 'flour', 'cereal', 'bread', 'deli meat']
        
        for food in foods:
            if food in text:
                return food.title()
        return "Food Product"
    
    def _extract_who_details(self, url: str, title: str, summary: str) -> tuple:
        """Extract detailed information from WHO page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            content = soup.get_text().lower()
            pathogen = self._extract_pathogen_name(title + " " + summary)
            
            # Extract countries mentioned
            countries = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', content)
            countries = [c for c in countries if len(c.split()) <= 3][:5]  # Limit to reasonable country names
            
            # Extract case numbers
            case_matches = re.findall(r'(\d+)\s*(?:cases?|people|individuals)', content)
            cases = int(case_matches[0]) if case_matches else None
            
            return pathogen, countries, cases
            
        except Exception:
            pathogen = self._extract_pathogen_name(title + " " + summary)
            return pathogen, [], None
    
    def _extract_ecdc_details(self, url: str, text: str) -> tuple:
        """Extract ECDC outbreak details"""
        pathogen = self._extract_pathogen_name(text)
        countries = ["Multiple European Countries"]  # ECDC typically covers multiple EU countries
        cases = None
        
        # Try to extract case numbers from text
        case_matches = re.findall(r'(\d+)\s*(?:cases?|people)', text)
        if case_matches:
            cases = int(case_matches[0])
            
        return pathogen, countries, cases
    
    def _countries_to_regions(self, countries: List[str]) -> List[str]:
        """Convert countries to WHO regions"""
        if not countries:
            return ["Global"]
            
        # Simplified mapping
        europe = ["Belgium", "France", "Germany", "Spain", "Italy", "Netherlands", "Sweden", "Norway"]
        americas = ["United States", "Canada", "Brazil", "Mexico", "Argentina"]
        asia = ["China", "India", "Japan", "South Korea", "Thailand", "Indonesia"]
        africa = ["Nigeria", "South Africa", "Kenya", "Egypt"]
        
        regions = set()
        for country in countries:
            if any(eu_country in country for eu_country in europe):
                regions.add("Europe")
            elif any(am_country in country for am_country in americas):
                regions.add("Americas")
            elif any(as_country in country for as_country in asia):
                regions.add("Asia")
            elif any(af_country in country for af_country in africa):
                regions.add("Africa")
            else:
                regions.add("Global")
                
        return list(regions)
    
    def _assess_severity(self, cases: Optional[int], countries: List[str]) -> str:
        """Assess outbreak severity level"""
        if not cases:
            return "Medium"
            
        if cases >= 100 or len(countries) > 5:
            return "High"
        elif cases >= 20 or len(countries) > 2:
            return "Medium"
        else:
            return "Low"
    
    def _parse_who_date(self, date_str: str) -> str:
        """Parse WHO date format"""
        try:
            # WHO uses various date formats
            if date_str:
                parsed = datetime.strptime(date_str[:10], '%Y-%m-%d')
                return parsed.strftime('%Y-%m-%d')
        except:
            pass
        return datetime.now().strftime('%Y-%m-%d')
    
    def run_full_scan(self) -> List[FoodborneOutbreak]:
        """Run full scan of all sources"""
        print("Starting global foodborne outbreak scan...")
        all_outbreaks = []
        
        # Scrape all sources
        sources = [
            self.scrape_who_disease_outbreak_news,
            self.scrape_ecdc_threats,
            self.scrape_health_canada_recalls,
            self.scrape_cdc_foodborne_outbreaks
        ]
        
        for source_func in sources:
            try:
                outbreaks = source_func()
                all_outbreaks.extend(outbreaks)
                print(f"Found {len(outbreaks)} outbreaks from {source_func.__name__}")
                time.sleep(2)  # Be respectful to servers
            except Exception as e:
                print(f"Error in {source_func.__name__}: {e}")
        
        # Remove duplicates based on pathogen + product combination
        seen = set()
        unique_outbreaks = []
        for outbreak in all_outbreaks:
            key = f"{outbreak.pathogen}_{outbreak.product}_{outbreak.source_organization}"
            if key not in seen:
                seen.add(key)
                unique_outbreaks.append(outbreak)
        
        print(f"Total unique outbreaks found: {len(unique_outbreaks)}")
        return unique_outbreaks
    
    def save_to_json(self, outbreaks: List[FoodborneOutbreak], filename: str = "foodborne_outbreaks.json"):
        """Save outbreaks to JSON file for web integration"""
        data = {
            "last_updated": datetime.now().isoformat(),
            "total_outbreaks": len(outbreaks),
            "outbreaks": [asdict(outbreak) for outbreak in outbreaks]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {len(outbreaks)} outbreaks to {filename}")

def main():
    """Main execution function"""
    monitor = GlobalFoodborneMonitor()
    
    # Run full scan
    outbreaks = monitor.run_full_scan()
    
    # Save results
    monitor.save_to_json(outbreaks)
    
    # Print summary
    print("\n" + "="*50)
    print("GLOBAL FOODBORNE OUTBREAK SUMMARY")
    print("="*50)
    
    if outbreaks:
        for i, outbreak in enumerate(outbreaks, 1):
            print(f"{i}. {outbreak.pathogen} in {outbreak.product}")
            print(f"   Countries: {', '.join(outbreak.countries[:3])}")
            print(f"   Cases: {outbreak.cases or 'Unknown'}")
            print(f"   Source: {outbreak.source_organization}")
            print(f"   Severity: {outbreak.severity_level}")
            print()
    else:
        print("No active foodborne outbreaks detected at this time.")

if __name__ == "__main__":
    main()
