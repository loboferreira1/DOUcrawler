import datetime
import re
import time
import yaml
import requests
import json
from urllib.parse import unquote

# Configuration
CONFIG_PATH = "config.yaml"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Headers - EXACT COPY of what works in production (from your logs/downloader.py)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Intentionally minimal to start, matching the base scraper if possible, 
    # but let's add the extra ones that were successful in your latest run.
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1"
}

def get_section_url(section: str, date: datetime.date) -> str:
    # Use the exact format from downloader.py
    date_str = date.strftime("%d-%m-%Y")
    return f"https://www.in.gov.br/leiturajornal?secao={section}&data={date_str}"

def fetch_content(url):
    print(f"Fetching {url}...")
    try:
        # Add delay and a session to maintain cookies
        session = requests.Session()
        session.headers.update(HEADERS)
        
        # First, visit the home page to set cookies
        print("Creating session (cookie handshake)...")
        session.get("https://www.in.gov.br/leiturajornal", timeout=30)
        time.sleep(3) # Wait for "rendering"
        
        response = session.get(url, timeout=60)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching: {e}")
        return None

def extract_urls_regex(html):
    # The regex from downloader.py
    regex_slug = re.compile(r'"urlTitle"\s*:\s*"([^"]+)"')
    slugs = regex_slug.findall(html)
    return list(set(slugs))

def filter_slugs(slugs, rules):
    # Simple keyword matching on the slug itself
    # e.g. "portaria-mjsp-123" matches "portaria mjsp"
    
    # Flatten search terms
    terms = []
    for r in rules:
        terms.extend([t.lower() for t in r.get("title_terms", [])])
    
    print(f"Filtering against terms: {terms}")
    
    matches = []
    for slug in slugs:
        # Normalize slug: "portaria-mjsp-n-123" -> "portaria mjsp n 123"
        normalized = unquote(slug).replace("-", " ").lower()
        
        for term in terms:
            if term in normalized:
                matches.append(slug)
                break
    return matches

def main():
    config = load_config()
    
    # Check TODAY first
    today = datetime.date.today()
    # If it's a weekend, maybe fallback to last Friday for testing pursposes?
    # but for now let's stick to today as requested "is a working day" check
    
    if today.weekday() >= 5: # 5=Sat, 6=Sun
        print(f"Today ({today}) is a weekend. Switching to last Friday for TEST.")
        days_to_subtract = today.weekday() - 4
        target_date = today - datetime.timedelta(days=days_to_subtract)
    else:
        target_date = today

    print(f"Target Date: {target_date}")
    
    section = "dou1" # Focus on dou1
    url = get_section_url(section, target_date)
    
    html = fetch_content(url)
    if not html:
        return

    # 1. Verification Phase
    slugs = extract_urls_regex(html)
    print(f"Found {len(slugs)} raw items via Regex.")
    
    if len(slugs) == 0:
        print("CRITICAL: No URLs found. Dumping snippet of HTML to see if 'urlTitle' exists...")
        if "urlTitle" in html:
            print("String 'urlTitle' IS present in HTML, but regex failed.")
            print(re.search(r'.{0,50}urlTitle.{0,50}', html).group(0))
        else:
            print("String 'urlTitle' is NOT present in HTML.")
        return

    # 2. Filtering Phase
    print(f"Sample slug: {slugs[0]}")
    
    matches = filter_slugs(slugs, config.get("rules", []))
    
    print(f"\nTotal potential downloads: {len(slugs)}")
    print(f"Filtered downloads (relevant): {len(matches)}")
    
    if len(matches) > 0:
        print("Example matches:")
        for m in matches[:5]:
            print(f" - https://www.in.gov.br/web/dou/-/{m}")
    else:
        print("No matches for your rules.")

if __name__ == "__main__":
    main()
