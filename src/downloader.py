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

# Imita um navegador padrão para evitar bloqueios
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_section_url(section: str, date: datetime.date) -> str:
    """
    Constrói a URL para uma seção específica do DOU e data.
    Args:
        section: 'dou1', 'dou2', 'dou3', etc.
        date: objeto datetime.date.
    Retorna:
        String URL completa como 'https://www.in.gov.br/leiturajornal?secao=dou1&data=DD-MM-YYYY'
    """
    date_str = date.strftime("%d-%m-%Y")
    return f"{URL_LEITURA}?secao={section}&data={date_str}"

def is_retryable_error(exception):
    """
    Retorna True se a exceção for um erro de rede repetível ou erro do servidor (5xx).
    Retorna False para erros 4xx (exceto 429 Too Many Requests).
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
    Busca o conteúdo de uma URL com tentativas repetidas.
    """
    logger.info("fetching_url", url=url)
    
    # Random sleep inside fetch_content itself, to throttle per-article requests
    import time
    import random
    time.sleep(random.uniform(5.0, 12.0))

    try:
        # Extra headers to mimic a real browser request even more closely
        extra_headers = {
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
        
        # Combine default headers (which might be updated by caller) with extra headers
        request_headers = {**HEADERS, **extra_headers}

        response = requests.get(url, headers=request_headers, timeout=60)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error("fetch_failed", url=url, error=str(e))
        raise

def fetch_article_urls(section: str, date: datetime.date) -> list[str]:
    """
    Busca todas as URLs de artigos para uma dada seção e data.
    Usa Regex para extrair dados JSON embutidos na página, o que é mais robusto
    para a página 'Leitura do Jornal' que usa renderização no lado do cliente.
    """
    start_url = get_section_url(section, date)
    collected_urls = set()
    current_url = start_url
    
    logger.info("start_crawling_section", section=section, date=str(date))
    
    # regex para "urlTitle": "slug-do-artigo"
    # Lida com variações potenciais de espaçamento
    regex_slug = re.compile(r'"urlTitle"\s*:\s*"([^"]+)"')
    
    try:
        html = fetch_content(current_url)
        
        # 1. Extração por Regex (Estratégia Primária para Dados)
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

