import pytest
from src import matcher
from src.models import MatchEntry

# Texto de ajuda
TEXT_SAMPLE = (
    "O Presidente da República resolve nomear João Silva para o cargo. "
    "A Fundação Nacional dos Povos Indígenas publicou nova portaria. "
    "Outro texto irrelevante aqui."
)

TEXT_SAMPLE_LOWER = "a ação da funai foi decisiva."
TEXT_SAMPLE_ACCENTS = "É necessário força nacional imediatamente."

def test_find_matches_exact_keyword():
    """Testa encontrar correspondência de palavra-chave simples."""
    matches = matcher.find_matches(
        text=TEXT_SAMPLE, 
        keywords=["Fundação Nacional dos Povos Indígenas"],
        date="10/02/2026",
        section="dou1",
        url="http://example.com"
    )
    
    assert len(matches) == 1
    assert matches[0].keyword == "Fundação Nacional dos Povos Indígenas"
    assert "publicou nova portaria" in matches[0].context

def test_find_matches_case_insensitive():
    """Testa encontrar correspondência ignorando maiúsculas/minúsculas."""
    matches = matcher.find_matches(
        text=TEXT_SAMPLE_LOWER,
        keywords=["FUNAI"],
        date="10/02/2026",
        section="dou1",
        url="http://example.com"
    )
    
    assert len(matches) == 1
    assert matches[0].keyword == "FUNAI" # Deve preservar caixa da keyword na config
    assert "da funai foi" in matches[0].context

def test_find_matches_accent_insensitive():
    """Testa encontrar correspondência ignorando acentos."""
    matches = matcher.find_matches(
        text=TEXT_SAMPLE_ACCENTS,
        keywords=["forca nacional"], # Config não tem acento
        date="10/02/2026",
        section="dou1",
        url="http://example.com"
    )
    
    assert len(matches) == 1
    assert matches[0].keyword == "forca nacional"
    assert "força nacional" in matches[0].context # Contexto preserva texto original

def test_find_matches_context_window_size():
    """Testa se o contexto extrai caracteres ao redor."""
    long_text = "start " + ("x" * 100) + " keyword " + ("y" * 100) + " end"
    matches = matcher.find_matches(
        text=long_text,
        keywords=["keyword"],
        date="today",
        section="s1",
        url="url"
    )
    
    assert len(matches) == 1
    context = matches[0].context
    assert "keyword" in context
    # Deve ter aproximadamente 150 caracteres no total ou 100 antes/depois?
    # Spec diz "~100-200 caracteres ao redor".
    # Vamos verificar se definitivamente captura algum contexto mas não o mundo todo se for enorme.
    assert len(context) > 20
    assert "x" * 20 in context
    assert "y" * 20 in context

def test_find_matches_no_match():
    """Testa nenhuma correspondência encontrada."""
    matches = matcher.find_matches(
        text="Nada relevante aqui.",
        keywords=["funai"],
        date="today",
        section="s1",
        url="url"
    )
    assert len(matches) == 0

def test_find_multiple_matches_same_keyword():
    """Testa se a mesma palavra-chave aparece duas vezes, obtemos correspondências (ou apenas uma?).
    Geralmente para um raspador, ocorrências distintas são boas, mas idempotência estrita pode filtrar.
    Vamos assumir que capturamos ocorrências.
    """
    text = "A funai fez isso. Depois a funai fez aquilo."
    matches = matcher.find_matches(
        text=text,
        keywords=["funai"],
        date="today",
        section="s1",
        url="url"
    )
    assert len(matches) == 2
    assert "fez isso" in matches[0].context
    assert "fez aquilo" in matches[1].context
