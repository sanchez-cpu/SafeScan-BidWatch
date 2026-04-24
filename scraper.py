import requests
from bs4 import BeautifulSoup
import re
import time
from database import save_bid

# === COMPREHENSIVE KEYWORDS FOR UTILITY LOCATING SERVICES ===
KEYWORDS = [
    # Official NIGP & Core Codes
    "96291", "utility locate", "utility locating", "underground locate", "utility locator",
    "811", "call before you dig", "line locating", "pre-excavation locate",
    "locating services", "utility marking", "underground utility", "pipe locating",
    
    # Common Bid Phrases
    "locating contract", "annual locating", "on-call locating", "locate ticket",
    "subsurface utility", "SUE", "utility coordination", "miss utility",
    "dig ticket", "excavation locating", "one call locate", "utility locator service",
    "professional locating", "locate and mark"
]

def scrape_site(url, agency):
    bids = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=40)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        items = soup.select("table tr, .project-card, .solicitation-row, .card, article, a, div")
        
        for item in items[:80]:
            try:
                text = item.get_text(strip=True)
                if len(text) < 15:
                    continue
                    
                link_tag = item.find("a")
                link = link_tag["href"] if link_tag else ""
                if link and not link.startswith("http"):
                    base = url[:url.find("/project-list")] if "/project-list" in url else url.rsplit("/", 1)[0]
                    link = base + "/" + link.lstrip("/")
                
                matched = [k for k in KEYWORDS if k.lower() in text.lower()]
                
                # Strong match if any keyword appears
                if matched or any(phrase in text.lower() for phrase in ["utility locate", "locating service", "96291"]):
                    bid_id = f"{agency[:12]}-{re.sub(r'[^a-zA-Z0-9]', '', text)[:60]}"
                    bid = {
                        "id": bid_id,
                        "title": text[:280],
                        "agency": agency,
                        "url": link or url,
                        "due_date": "",
                        "description": "",
                        "keywords_matched": ", ".join(matched)
                    }
                    if save_bid(bid):
                        bids.append(bid)
            except:
                continue
    except Exception as e:
        print(f"Error scraping {agency}: {e}")
    return bids

def run_scraper():
    print("🚀 Starting BidWatch — Utility Locating Services (Expanded Florida Search)...")
    all_new = []
    
    # === GREATLY EXPANDED LIST OF FLORIDA COUNTIES & CITIES ===
    targets = [
        # Major Counties (OpenGov)
        ("https://procurement.opengov.com/portal/alachuacounty/project-list", "Alachua County"),
        ("https://procurement.opengov.com/portal/orangecountyfl/project-list", "Orange County"),
        ("https://procurement.opengov.com/portal/santarosafl/project-list", "Santa Rosa County"),
        ("https://procurement.opengov.com/portal/leoncounty/project-list", "Leon County"),
        ("https://procurement.opengov.com/portal/hernandocounty/project-list", "Hernando County"),
        ("https://procurement.opengov.com/portal/pinellasfl/project-list", "Pinellas County"),
        ("https://procurement.opengov.com/portal/scgov/project-list", "Sarasota County"),
        ("https://procurement.opengov.com/portal/claycounty/project-list", "Clay County"),
        ("https://procurement.opengov.com/portal/duvalcounty/project-list", "Duval County"),
        ("https://procurement.opengov.com/portal/broward/project-list", "Broward County"),
        ("https://procurement.opengov.com/portal/miamidade/project-list", "Miami-Dade County"),
        ("https://procurement.opengov.com/portal/volusia/project-list", "Volusia County"),
        ("https://procurement.opengov.com/portal/flagler/project-list", "Flagler County"),
        ("https://procurement.opengov.com/portal/waltoncountyfl/project-list", "Walton County"),
        ("https://procurement.opengov.com/portal/collier/project-list", "Collier County"),
        ("https://procurement.opengov.com/portal/hillsborough/project-list", "Hillsborough County"),
        ("https://procurement.opengov.com/portal/palmbeach/project-list", "Palm Beach County"),
        
        # Additional Cities & Others
        ("https://procurement.ufl.edu/vendors/schedule-of-bids/", "University of Florida"),
        ("https://www.cityofarcher.com/rfps", "City of Archer"),
        # You can keep adding more here (e.g. Gainesville, Newberry, etc.)
    ]
    
    for url, agency in targets:
        print(f"Scanning {agency} for locating services...")
        new_bids = scrape_site(url, agency)
        all_new.extend(new_bids)
        time.sleep(3)
    
    print(f"✅ Scan complete! Found {len(all_new)} new potential locating bids.")
    return all_new