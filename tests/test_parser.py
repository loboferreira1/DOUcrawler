import pytest
from src import parser

# Sample HTML data
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
    """Test extracting title from <title> tag."""
    title = parser.extract_title(HTML_WITH_TITLE)
    assert title == "Portaria 123 - DOU"

def test_extract_title_fallback_empty():
    """Test handling missing title (returns empty string or None)."""
    # Assuming implementation returns empty string if not found, based on simple return type str
    title = parser.extract_title("<html><body>No title</body></html>")
    assert title == ""

def test_extract_text_cleans_tags_and_scripts():
    """Test removing script, style, html tags."""
    text = parser.extract_text(HTML_DIRTY)
    assert "alert" not in text
    assert "color: red" not in text
    assert "Texto com muitos espaços." in text
    assert "Outro parágrafo." in text
    # Verify whitespace normalization
    assert "Texto com muitos espaços. Outro parágrafo." in " ".join(text.split())

def test_extract_text_preserves_accents():
    """
    Storage requirement: Preserve Portuguese accents.
    Parser.extract_text should return text WITH accents.
    """
    text = parser.extract_text(HTML_WITH_ACCENTS)
    assert "Fundação Nacional dos Povos Indígenas" in text

def test_normalize_text_removes_accents():
    """
    Search requirement: Compare accent-insensitive.
    Parser should provide normalization logic.
    """
    raw = "Fundação Nacional dos Povos Indígenas"
    normalized = parser.normalize_text(raw)
    
    # NFD decomposition + filtering non-spacing marks usually results in ASCII-like text
    # or at least separated chars.
    # For simple case-insensitive accent-insensitive match:
    # "fundacao" in "fundação" (normalized)
    
    # Let's verify it matches our expectation for "indigena" matching "indígena"
    assert "indigena" in normalized
    assert "fundacao" in normalized
    assert normalized == "fundacao nacional dos povos indigenas" # Assuming lowercase too? 
    # Spec says "Case-insensitive + accent-insensitive". 
    # Usually normalize() does only accent stripping, but for search helper it might do lower().
    # Let's assume strict accent stripping only for now, or commonly both.
    # Let's enforce lower() + accent stripping for specific 'normalize_text' helper intended for matching.
    
    assert parser.normalize_text("Árvore") == "arvore"
