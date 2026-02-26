import datetime
import re
import time
import sys
import yaml
import requests
import json
from urllib.parse import unquote

# Configuration
CONFIG_PATH = "config.yaml"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Headers (mirrored from src/downloader.py)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1"
}

def get_section_url(section: str, date: datetime.date) -> str:
    date_str = date.strftime("%d-%m-%Y")
    return f"https://www.in.gov.br/leiturajornal?secao={section}&data={date_str}"

def fetch_with_retry(url):
    retries = 3
    for i in range(retries):
        try:
            print(f"Fetching {url} (Attempt {i+1})...")
            response = requests.get(url, headers=HEADERS, timeout=60)
            
            if response.status_code == 200:
                print(f"Success! Content length: {len(response.text)}")
                return response.text
            elif response.status_code in [500, 502, 503, 504]:
                print(f"Server error {response.status_code}. Retrying...")
                time.sleep(5)
            else:
                print(f"Client error {response.status_code}.")
                return None
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
    return None

def is_working_day(date: datetime.date):
    # Simple check: Monday (0) to Friday (4)
    # TODO: Add holiday check
    return date.weekday() < 5

def extract_urls(html):
    # Regex to find JSON-like structures with urlTitle
    # We try to grab the title if possible, but the current reliable method is just the slug
    regex_slug = re.compile(r'"urlTitle"\s*:\s*"([^"]+)"')
    slugs = regex_slug.findall(html)
    unique_slugs = sorted(list(set(slugs)))
    
    full_urls = [f"https://www.in.gov.br/web/dou/-/{slug}" for slug in unique_slugs]
    return full_urls

def filter_urls(urls, rules):
    filtered = []
    
    # Flatten all title terms from all rules for this test
    # In a real scenario, we'd map terms to specific rules, but here we just want to know "pass" or "fail"
    target_terms = []
    for rule in rules:
        target_terms.extend([t.lower() for t in rule.get("title_terms", [])])
    
    print(f"\nFiltering {len(urls)} URLs against terms: {target_terms}")

    for url in urls:
        # Check if any term is in the URL slug (normalized)
        slug = url.split("/-/")[-1].lower()
        slug_readable = unquote(slug).replace("-", " ")
        
        # Check against terms
        matched = False
        for term in target_terms:
            if term in slug_readable:
                filtered.append((url, term))
                matched = True
                break
        
    return filtered

def main():
    config = load_config()
    print("Loaded configuration.")
    
    # Use today's date or specific date
    date_to_check = datetime.date.today()
    # date_to_check = datetime.date(2025, 2, 26) # Uncomment to test specific date
    
    print(f"Date: {date_to_check}")
    
    if not is_working_day(date_to_check):
        print("Warning: Today is a weekend. Documents might not be available.")
    
    rules = config.get("rules", [])
    sections = set()
    for rule in rules:
        sections.update(rule.get("sections", ["dou1"]))
    
    total_discovered = 0
    all_filtered = []

    for section in sections:
        url = get_section_url(section, date_to_check)
        print(f"\n--- Processing Section: {section} ---")
        
        html = fetch_with_retry(url)
        if not html:
            print("Failed to fetch section page.")
            continue
            
        urls = extract_urls(html)
        print(f"Discovered {len(urls)} documents in {section}.")
        
        if len(urls) == 0:
            if is_working_day(date_to_check):
                print("CRITICAL: No documents found on a working day. Possible parsing error or blockers.")
                # Save HTML for debugging
                with open(f"debug_{section}.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"Saved HTML to debug_{section}.html")
            else:
                print("No documents found, but it is a weekend/holiday.")
        
        filtered = filter_urls(urls, rules)
        print(f"Keep {len(filtered)} / {len(urls)} documents.")
        
        all_filtered.extend(filtered)
        total_discovered += len(urls)

    print("\n=== SUMMARY ===")
    print(f"Total Discovered: {total_discovered}")
    print(f"Total Matches (to be downloaded): {len(all_filtered)}")
    
    if len(all_filtered) > 0:
        print("\nMatches Preview:")
        for url, term in all_filtered[:10]:
            print(f"[{term}] {url}")

if __name__ == "__main__":
    main()
