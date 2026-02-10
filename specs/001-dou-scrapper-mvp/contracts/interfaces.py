from typing import List, Protocol, Optional, Dict, Any
from datetime import date

class IDownloader(Protocol):
    def fetch_edition_links(self, target_date: date, section_slug: str) -> List[str]:
        """
        Fetches the list of article URLs for a given date and section.
        Returns a list of absolute URLs.
        """
        ...

    def fetch_article_content(self, url: str) -> str:
        """
        Fetches the full HTML content of a single article.
        """
        ...

class IParser(Protocol):
    def extract_text(self, html_content: str) -> str:
        """
        Extracts clean text from article HTML.
        """
        ...
    
    def extract_title(self, html_content: str) -> str:
        """
        Extracts title from article HTML.
        """
        ...

class IMatcher(Protocol):
    def find_matches(self, text: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Searches text for keywords.
        Returns list of dicts: {'keyword': str, 'context': str}
        """
        ...

class IStorage(Protocol):
    def save_match(self, match_data: Dict[str, Any]) -> None:
        """
        Persists a match entry to storage (file/db).
        """
        ...
