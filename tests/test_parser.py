import pytest
from src import parser

# Dados HTML de exemplo
HTML_WITH_TITLE = """
<html>
    <head><title>Portaria 123 - DOU</title></head>
    <body><p>Conteúdo da portaria.</p></body>
</html>
"""

HTML_WITHOUT_TITLE = """
<html>
    <body><h1>Título no H1</h1><p>Conteúdo.</p></body>
</html>
"""

HTML_DIRTY = """
<html>
    <head>
        <style>body { color: red; }</style>
        <script>alert('hello');</script>
    </head>
    <body>
        <p>Texto    com   muitos   espaços.</p>
        <br>
        <div>Outro parágrafo.</div>
        <!-- Comentário -->
    </body>
</html>
"""

HTML_WITH_ACCENTS = """
<html><body><p>Atos da Fundação Nacional dos Povos Indígenas.</p></body></html>
"""

def test_extract_title_from_head_tag():
    """Testa extração de título da tag <title>."""
    title = parser.extract_title(HTML_WITH_TITLE)
    assert title == "Portaria 123 - DOU"

def test_extract_title_fallback_empty():
    """Testa tratamento de título ausente (retorna string vazia ou None)."""
    # Assumindo que a implementação retorna string vazia se  não encontrado, baseado no tipo de retorno simples str
    title = parser.extract_title("<html><body>No title</body></html>")
    assert title == ""

def test_extract_text_cleans_tags_and_scripts():
    """Testa remoção de tags script, style, html."""
    text = parser.extract_text(HTML_DIRTY)
    assert "alert" not in text
    assert "color: red" not in text
    assert "Texto com muitos espaços." in text
    assert "Outro parágrafo." in text
    # Verifica normalização de espaço em branco
    assert "Texto com muitos espaços. Outro parágrafo." in " ".join(text.split())

def test_extract_text_preserves_accents():
    """
    Requisito de armazenamento: Preservar acentos portugueses.
    Parser.extract_text deve retornar texto COM acentos.
    """
    text = parser.extract_text(HTML_WITH_ACCENTS)
    assert "Fundação Nacional dos Povos Indígenas" in text

def test_normalize_text_removes_accents():
    """
    Requisito de pesquisa: Comparar insensível a acentos.
    O parser deve fornecer lógica de normalização.
    """
    raw = "Fundação Nacional dos Povos Indígenas"
    normalized = parser.normalize_text(raw)
    
    # Decomposição NFD + filtragem de marcas sem espaçamento geralmente resulta em texto semelhante a ASCII
    # ou pelo menos caracteres separados.
    # Para correspondência simples insensível a maiúsculas/minúsculas e acentos:
    # "fundacao" em "fundação" (normalizado)
    
    # Vamos verificar se corresponde à nossa expectativa para "indigena" combinando com "indígena"
    assert "indigena" in normalized
    assert "fundacao" in normalized
    assert normalized == "fundacao nacional dos povos indigenas" # Assumindo minúsculas também?
    # Spec diz "Insensível a maiúsculas/minúsculas + insensível a acentos".
    # Geralmente normalize() faz apenas remoção de acentos, mas para ajudante de pesquisa pode fazer lower().
    # Vamos assumir remoção estrita de acentos apenas por enquanto, ou comumente ambos.
    # Vamos impor lower() + remoção de acentos para o ajudante específico 'normalize_text' destinado à correspondência.
    
    assert parser.normalize_text("Árvore") == "arvore"
