import re
import datetime
import requests
import structlog
import time
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

class DiscoveryService:
    def __init__(self, config):
        self.config = config
        self.base_url = "https://www.in.gov.br/leiturajornal"
        # Headers copied EXACTLY from working src/downloader.py
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }

    def _get_section_url(self, section: str, date: datetime.date) -> str:
        date_str = date.strftime("%d-%m-%Y")
        return f"{self.base_url}?secao={section}&data={date_str}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_section_page(self, section: str, date: datetime.date) -> str:
        url = self._get_section_url(section, date)
        logger.info("discovery_fetch_start", url=url)
        
        # Initial handshake to set cookies if needed
        session = requests.Session()
        session.headers.update(self.headers)
        
        try:
            response = session.get(url, timeout=45)
            response.raise_for_status()
            
            # Simple validation: is this actually the Leitura Jornal page?
            if "Leitura dos Jornais" not in response.text and "jsonArray" not in response.text:
                logger.warning("discovery_suspicious_content", url=url, length=len(response.text))
            
            return response.text
        except requests.RequestException as e:
            logger.error("discovery_fetch_error", error=str(e))
            raise

    def extract_urls(self, html: str) -> list[str]:
        # Primary method: Regex for the JSON data blob
        regex = re.compile(r'"urlTitle"\s*:\s*"([^"]+)"')
        slugs = regex.findall(html)
        
        unique_slugs = sorted(list(set(slugs)))
        
        # Construct full URLs
        return [f"https://www.in.gov.br/web/dou/-/{slug}" for slug in unique_slugs]

    def filter_urls(self, urls: list[str]) -> list[tuple[str, str]]:
        """
        Returns a list of (url, matched_rule_name) tuples.
        """
        rules = self.config.get("rules", [])
        kept = []
        
        # Pre-process rules for faster matching
        rule_map = []
        for r in rules:
            terms = [t.lower() for t in r.get("title_terms", [])]
            if terms:
                rule_map.append((r["name"], terms))
        
        if not rule_map:
            logger.warning("no_title_rules_defined", msg="Returning all URLs")
            return [(u, "wildcard") for u in urls]

        for url in urls:
            # Extract slug from URL for matching
            # https://.../web/dou/-/imoveis-da-uniao-123 -> "imoveis da uniao 123"
            slug_part = url.split("/-/")[-1].replace("-", " ").lower()
            
            for rule_name, terms in rule_map:
                for term in terms:
                    if term in slug_part:
                        kept.append((url, rule_name))
                        break # Matched this rule, stop checking other terms for this rule
                else:
                    continue # Check next rule
                break # Matched a rule, move to next URL

        return kept

    def run_discovery(self, date: datetime.date = None):
        if date is None:
            date = datetime.date.today()
            
        logger.info("discovery_start", date=str(date))
        
        # 1. Check if working day
        if date.weekday() >= 5:
            logger.info("discovery_weekend_check", msg="It is a weekend. Expect few or no results.")

        all_valid_urls = []
        
        # Iterate through relevant sections defined in rules
        target_sections = set()
        for r in self.config.get("rules", []):
            target_sections.update(r.get("sections", ["dou1"]))
            
        for section in target_sections:
            try:
                html = self.fetch_section_page(section, date)
                raw_urls = self.extract_urls(html)
                
                if not raw_urls:
                    logger.warning("discovery_no_urls_found", section=section)
                    # Here we could implement fallback logic or deeper error checking
                    continue
                
                logger.info("discovery_raw_count", section=section, count=len(raw_urls))
                
                filtered = self.filter_urls(raw_urls)
                logger.info("discovery_filtered_count", section=section, count=len(filtered))
                
                all_valid_urls.extend(filtered)
                
            except Exception as e:
                logger.error("discovery_section_failed", section=section, error=str(e))
        
        return all_valid_urls

# Standalone execution for testing
if __name__ == "__main__":
    import yaml
    import sys
    import logging

    # Configure basic logging to stdout
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    structlog.configure(
        processors=[
            structlog.processors.JSONRenderer(indent=2, sort_keys=True)
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("Config file not found.")
        sys.exit(1)

    service = DiscoveryService(config)
    
    print("\n--- Starting Discovery (Dry Run) ---")
    results = service.run_discovery()
    
    print(f"\n--- Final Results: {len(results)} Documents to Download ---")
    for url, rule in results[:20]:
        print(f"[{rule}] {url}")
    
    if len(results) > 20:
        print(f"... and {len(results)-20} more.")
