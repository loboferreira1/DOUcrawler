import re
import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

logger = structlog.get_logger()

BASE_URL = "https://www.in.gov.br"
URL_LEITURA = f"{BASE_URL}/leiturajornal"

# Mimic a standard browser to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_section_url(section: str, date: datetime.date) -> str:
    """
    Constructs the URL for a specific DOU section and date.
    Args:
        section: 'dou1', 'dou2', 'dou3', etc.
        date: datetime.date object.
    Returns:
        Full URL string like 'https://www.in.gov.br/leiturajornal?secao=dou1&data=DD-MM-YYYY'
    """
    date_str = date.strftime("%d-%m-%Y")
    return f"{URL_LEITURA}?secao={section}&data={date_str}"

def is_retryable_error(exception):
    """
    Returns True if the exception is a retryable network error or server error (5xx).
    Returns False for 4xx errors (except 429 Too Many Requests).
    """
    if isinstance(exception, requests.HTTPError):
        if exception.response is not None:
            status_code = exception.response.status_code
            if status_code == 429:
                return True
            if 400 <= status_code < 500:
                return False
    return isinstance(exception, requests.RequestException)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception(is_retryable_error),
    reraise=True
)
def fetch_content(url: str) -> str:
    """
    Fetches the content of a URL with retries.
    """
    logger.info("fetching_url", url=url)
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error("fetch_failed", url=url, error=str(e))
        raise

def fetch_article_urls(section: str, date: datetime.date) -> list[str]:
    """
    Fetches all article URLs for a given section and date.
    Uses Regex to extract JSON data embedded in the page, which is more robust
    for the 'Leitura do Jornal' page which uses client-side rendering.
    """
    start_url = get_section_url(section, date)
    collected_urls = set()
    current_url = start_url
    
    logger.info("start_crawling_section", section=section, date=str(date))
    
    # regex for "urlTitle": "slug-of-article"
    # Handles potential spacing variations
    regex_slug = re.compile(r'"urlTitle"\s*:\s*"([^"]+)"')
    
    try:
        html = fetch_content(current_url)
        
        # 1. Regex Extraction (Primary Strategy for Data)
        slugs = regex_slug.findall(html)
        logger.info("regex_extraction", count=len(slugs), url=current_url)
        
        for slug in slugs:
             full_url = f"https://www.in.gov.br/web/dou/-/{slug}"
             collected_urls.add(full_url)
        
    except Exception as e:
        logger.error("crawl_step_failed", url=current_url, error=str(e))
        raise e

    logger.info("finished_crawling_section", total_urls=len(collected_urls))
    return list(collected_urls)

