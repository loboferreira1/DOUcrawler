import pytest
from src import matcher
from src.models import MatchEntry

# Helper text
TEXT_SAMPLE = (
    "O Presidente da República resolve nomear João Silva para o cargo. "
    "A Fundação Nacional dos Povos Indígenas publicou nova portaria. "
    "Outro texto irrelevante aqui."
)

TEXT_SAMPLE_LOWER = "a ação da funai foi decisiva."
TEXT_SAMPLE_ACCENTS = "É necessário força nacional imediatamente."

def test_find_matches_exact_keyword():
    """Test finding a simple keyword match."""
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
    """Test finding match ignoring case."""
    matches = matcher.find_matches(
        text=TEXT_SAMPLE_LOWER,
        keywords=["FUNAI"],
        date="10/02/2026",
        section="dou1",
        url="http://example.com"
    )
    
    assert len(matches) == 1
    assert matches[0].keyword == "FUNAI" # Should preserve config keyword casing
    assert "da funai foi" in matches[0].context

def test_find_matches_accent_insensitive():
    """Test finding match ignoring accents."""
    matches = matcher.find_matches(
        text=TEXT_SAMPLE_ACCENTS,
        keywords=["forca nacional"], # Config has no accent
        date="10/02/2026",
        section="dou1",
        url="http://example.com"
    )
    
    assert len(matches) == 1
    assert matches[0].keyword == "forca nacional"
    assert "força nacional" in matches[0].context # Context preserves original text

def test_find_matches_context_window_size():
    """Test that context extracts surrounding chars."""
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
    # Should have roughly 150 chars total or 100 before/after?
    # Spec says "~100-200 chars around". 
    # Let's verify it definitely grabs some context but not the whole world if huge.
    assert len(context) > 20
    assert "x" * 20 in context
    assert "y" * 20 in context

def test_find_matches_no_match():
    """Test no matches found."""
    matches = matcher.find_matches(
        text="Nada relevante aqui.",
        keywords=["funai"],
        date="today",
        section="s1",
        url="url"
    )
    assert len(matches) == 0

def test_find_multiple_matches_same_keyword():
    """Test if same keyword appears twice, we get matches (or just one?).
    Usually for a scrapper, distinct occurrences are good, but strict idempotency might filter.
    Let's assume we capture occurrences.
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
