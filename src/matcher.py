from datetime import datetime
from typing import List

from .models import MatchEntry, AdvancedMatchRule
from .parser import normalize_text

CONTEXT_PADDING = 150

def find_matches(
    text: str, 
    keywords: List[str], 
    date: str, 
    section: str, 
    url: str,
    title: str = "",
    rules: List[AdvancedMatchRule] = None
) -> List[MatchEntry]:
    """
    Pesquisa por palavras-chave no texto fornecido (insensível a maiúsculas/acentos).
    Aceita lista simples de keywords E lista de regras avançadas.
    Retorna uma lista de objetos MatchEntry para cada ocorrência encontrada.
    """
    matches: List[MatchEntry] = []
    
    # Pré-normaliza para pesquisa
    searchable_text = normalize_text(text)
    
    # --- 1. Processamento de Keywords Simples ---
    for kw in keywords:
        searchable_kw = normalize_text(kw)
        if not searchable_kw:
            continue
            
        start_search_idx = 0
        while True:
            try:
                idx = searchable_text.index(searchable_kw, start_search_idx)
                
                # Extrai contexto do texto ORIGINAL
                start_context = max(0, idx - CONTEXT_PADDING)
                end_context = min(len(text), idx + len(kw) + CONTEXT_PADDING)
                context_slice = text[start_context:end_context]
                
                matches.append(MatchEntry(
                    keyword=kw,
                    context=context_slice,
                    date=date,
                    section=section,
                    url=url,
                    title=title,
                    capture_timestamp=datetime.now().isoformat()
                ))
                
                start_search_idx = idx + len(searchable_kw)
                
            except ValueError:
                break

    # --- 2. Processamento de Regras Avançadas ---
    if rules:
        normalized_title = normalize_text(title)
        
        for rule in rules:
            # Verifica filtro de título (se houver termos definidos)
            title_match_found = False
            
            if rule.title_terms:
                for term in rule.title_terms:
                    # Se achar QUALQUER termo no título, é match de título (lógica OR no título)
                    if normalize_text(term) in normalized_title:
                        title_match_found = True
                        break
                
                # Se regra exige termos de título e nenhum foi encontrado, descarta a regra
                if not title_match_found:
                    continue 

            # Se a regra NÃO tem body terms, e passou no title_terms, é match
            if not rule.body_terms:
                matches.append(MatchEntry(
                    keyword=rule.name,
                    context=f"Alerta de Título: {title}",
                    date=date,
                    section=section,
                    url=url,
                    title=title,
                    capture_timestamp=datetime.now().isoformat()
                ))
                continue

            # Se tem body terms, busca no corpo
            for term in rule.body_terms:
                searchable_term = normalize_text(term)
                if not searchable_term:
                    continue

                start_search_idx = 0
                while True:
                    try:
                        idx = searchable_text.index(searchable_term, start_search_idx)
                        
                        start_context = max(0, idx - CONTEXT_PADDING)
                        end_context = min(len(text), idx + len(term) + CONTEXT_PADDING)
                        context_slice = text[start_context:end_context]
                        
                        matches.append(MatchEntry(
                            keyword=rule.name, # Usa o nome da regra como keyword principal
                            context=context_slice,
                            date=date,
                            section=section,
                            url=url,
                            title=title,
                            capture_timestamp=datetime.now().isoformat()
                        ))
                        
                        start_search_idx = idx + len(searchable_term)
                    except ValueError:
                        break

    return matches
