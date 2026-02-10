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
    Searches for keywords in the provided text (case/accent insensitive).
    Returns a list of MatchEntry objects for every occurrence found.
    """
    matches: List[MatchEntry] = []
    
    # Pre-normalize for searching
    searchable_text = normalize_text(text)
    
    for kw in keywords:
        searchable_kw = normalize_text(kw)
        if not searchable_kw:
            continue
            
        start_search_idx = 0
        while True:
            try:
                # Find keyword index in normalized text
                idx = searchable_text.index(searchable_kw, start_search_idx)
                
                # Extract context from ORIGINAL text using the same index
                # (Assuming NFD normalization roughly preserves character count/positions for Latin script, 
                # which is generally true for simple accent strip. 
                # Be careful: if normalization changes length (e.g. ligatures), indices might drift.
                # However, strict NFD -> filtering non-spacing marks preserves base chars count.)
                
                start_context = max(0, idx - CONTEXT_PADDING)
                end_context = min(len(text), idx + len(kw) + CONTEXT_PADDING) # Use kw length from original or searchable?
                # Using searchable_kw length is safer for index math on searchable_text, 
                # but applied to original text it might be slightly off if accents were stripped.
                # Use length of match in searchable text for advancing index.
                
                # Context slice from original text
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
                
                # Advance search
                start_search_idx = idx + len(searchable_kw)
                
            except ValueError:
                # No more matches for this keyword
                break
                
    return matches
