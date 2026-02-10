import pytest
import datetime
from unittest.mock import MagicMock, call
import requests
import responses
from src import downloader

# Respostas de exemplo com JSON embutido em tags script (correspondendo ao comportamento real do site)
HTML_LIST_PAGE_JSON = """
<html>
    <head>
        <script id="params" type="application/json">
        {
            "jsonArray": [
                {"urlTitle": "portaria-manual-1", "title": "Portaria 1"},
                {"urlTitle": "decreto-manual-2", "title": "Decreto 2"},
                {"urlTitle": "aviso-manual-3", "title": "Aviso 3"}
            ]
        }
        </script>
    </head>
    <body>
        <div id="root"></div>
    </body>
</html>
"""

@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps

def test_generate_daily_url():
    """Testa a geração de URL para diferentes seções e datas."""
    date = datetime.date(2026, 2, 10)
    
    url_s1 = downloader.get_section_url("dou1", date)
    assert url_s1 == "https://www.in.gov.br/leiturajornal?secao=dou1&data=10-02-2026"
    
    url_s3 = downloader.get_section_url("dou3", date)
    assert "secao=dou3" in url_s3
    assert "data=10-02-2026" in url_s3

def test_fetch_article_urls_success(mocked_responses):
    """Testa a busca de URLs de artigos usando extração por Regex."""
    date = datetime.date(2026, 2, 10)
    base_url = "https://www.in.gov.br/leiturajornal?secao=dou1&data=10-02-2026"

    mocked_responses.add(
        responses.GET,
        base_url,
        body=HTML_LIST_PAGE_JSON,
        status=200
    )

    urls = downloader.fetch_article_urls("dou1", date)

    assert len(urls) == 3
    assert "https://www.in.gov.br/web/dou/-/portaria-manual-1" in urls
    assert "https://www.in.gov.br/web/dou/-/decreto-manual-2" in urls
    assert "https://www.in.gov.br/web/dou/-/aviso-manual-3" in urls

def test_fetch_article_urls_empty(mocked_responses):
    """Testa a busca em um dia sem edição (ou vazia)."""
    date = datetime.date(2026, 2, 10)
    url = "https://www.in.gov.br/leiturajornal?secao=dou1&data=10-02-2026"
    
    mocked_responses.add(
        responses.GET,
        url,
        body="<html><body>No articles</body></html>",
        status=200
    )
    
    urls = downloader.fetch_article_urls("dou1", date)
    assert urls == []

def test_fetch_content_success(mocked_responses):
    """Testa a busca de conteúdo de artigo único."""
    url = "https://www.in.gov.br/test-article"
    html = "<html>Content</html>"
    
    mocked_responses.add(responses.GET, url, body=html, status=200)
    
    content = downloader.fetch_content(url)
    assert content == html

def test_fetch_content_retry_logic(mocked_responses):
    """Testa se rede tenta novamente em erros 5xx."""
    url = "https://www.in.gov.br/retry-me"
    
    # Falha duas vezes, sucesso na terceira
    mocked_responses.add(responses.GET, url, status=500)
    mocked_responses.add(responses.GET, url, status=502)
    mocked_responses.add(responses.GET, url, body="ok", status=200)
    
    content = downloader.fetch_content(url)
    assert content == "ok"
    assert len(mocked_responses.calls) == 3

def test_fetch_content_404_logic(mocked_responses):
    """Testa se 404 não deve tentar repetidamente infinitamente mas lançar erro? Ou retornar None?
    Especificação disse 'Repetir em falhas de rede', 'Saída silenciosa em Sem Edição'.
    Para artigo individual 404, provavelmente queremos apenas pular ou falhar rápido.
    Vamos assumir falha rápida por enquanto para capturarmos links quebrados.
    """
    url = "https://www.in.gov.br/missing"
    mocked_responses.add(responses.GET, url, status=404)
    
    with pytest.raises(requests.exceptions.HTTPError):
        downloader.fetch_content(url)
