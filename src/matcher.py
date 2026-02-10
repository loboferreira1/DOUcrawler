from datetime import datetime
from typing import List

from .models import MatchEntry
from .parser import normalize_text

CONTEXT_PADDING = 150

def find_matches(
    text: str, 
    keywords: List[str], 
    date: str, 
    section: str, 
    url: str,
    title: str = ""
) -> List[MatchEntry]:
    """
    Pesquisa por palavras-chave no texto fornecido (insensível a maiúsculas/acentos).
    Retorna uma lista de objetos MatchEntry para cada ocorrência encontrada.
    """
    matches: List[MatchEntry] = []
    
    # Pré-normaliza para pesquisa
    searchable_text = normalize_text(text)
    
    for kw in keywords:
        searchable_kw = normalize_text(kw)
        if not searchable_kw:
            continue
            
        start_search_idx = 0
        while True:
            try:
                # Encontra índice da palavra-chave no texto normalizado
                idx = searchable_text.index(searchable_kw, start_search_idx)
                
                # Extrai contexto do texto ORIGINAL usando o mesmo índice
                # (Assumindo que a normalização NFD preserva aproximadamente a contagem/posições de caracteres para escrita latina,
                # o que é geralmente verdade para remoção simples de acentos.
                # Tenha cuidado: se a normalização alterar o comprimento (por exemplo, ligaduras), os índices podem desviar.
                # No entanto, estrito NFD -> filtragem de marcas sem espaçamento preserva a contagem de caracteres base.)
                
                start_context = max(0, idx - CONTEXT_PADDING)
                end_context = min(len(text), idx + len(kw) + CONTEXT_PADDING) # Usar comprimento de kw original ou pesquisável?
                # Usar comprimento de searchable_kw é mais seguro para matemática de índice em searchable_text,
                # mas aplicado ao texto original pode estar ligeiramente errado se acentos foram removidos.
                # Usa comprimento da correspondência no texto pesquisável para avançar o índice.
                
                # Fatia de contexto do texto original
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
                
                # Avança pesquisa
                start_search_idx = idx + len(searchable_kw)
                
            except ValueError:
                # Sem mais correspondências para esta palavra-chave
                break
                
    return matches
