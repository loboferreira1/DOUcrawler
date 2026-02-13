import pytest
from src import matcher
from src.models import AdvancedMatchRule

def test_rule_title_and_body_match():
    """Testa regra que exige match no título E no corpo."""
    rule = AdvancedMatchRule(
        name="Regra Composta",
        title_terms=["PORTARIA MJSP"],
        body_terms=["força nacional"]
    )
    
    # Caso de Sucesso
    matches = matcher.find_matches(
        text="O texto fala sobre o emprego da força nacional em algum lugar.",
        keywords=[],
        date="today",
        section="s1",
        url="u",
        title="PORTARIA MJSP Nº 123", # Título contém o termo
        rules=[rule]
    )
    assert len(matches) == 1
    assert matches[0].keyword == "Regra Composta"

    # Caso de Falha (Título errado)
    matches_fail_title = matcher.find_matches(
        text="O texto fala sobre o emprego da força nacional em algum lugar.",
        keywords=[],
        date="today",
        section="s1",
        url="u",
        title="OUTRO DECRETO",
        rules=[rule]
    )
    assert len(matches_fail_title) == 0

    # Caso de Falha (Corpo errado)
    matches_fail_body = matcher.find_matches(
        text="Texto irrelevante.",
        keywords=[],
        date="today",
        section="s1",
        url="u",
        title="PORTARIA MJSP Nº 123",
        rules=[rule]
    )
    assert len(matches_fail_body) == 0

def test_rule_title_only():
    """Testa regra que exige apenas match no título."""
    rule = AdvancedMatchRule(
        name="Apenas Título",
        title_terms=["AVISO DE LICITAÇÃO"],
        body_terms=[]
    )
    
    matches = matcher.find_matches(
        text="Texto qualquer.",
        keywords=[],
        date="today",
        section="s1",
        url="u",
        title="AVISO DE LICITAÇÃO Nº 500",
        rules=[rule]
    )
    assert len(matches) == 1
    assert "Alerta de Título" in matches[0].context

def test_rule_body_only():
    """Testa regra que exige apenas match no corpo (comportamento de keyword avançada)."""
    rule = AdvancedMatchRule(
        name="Apenas Corpo",
        title_terms=[],
        body_terms=["importante"]
    )
    
    matches = matcher.find_matches(
        text="Este é um texto muito importante para ler.",
        keywords=[],
        date="today",
        section="s1",
        url="u",
        title="Título X",
        rules=[rule]
    )
    assert len(matches) == 1
    assert matches[0].keyword == "Apenas Corpo"
    assert "importante" in matches[0].context